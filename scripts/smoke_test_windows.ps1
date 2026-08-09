[CmdletBinding()]
param(
    [string]$PackagePath = "",
    [int]$RunSeconds = 15,
    [switch]$KeepArtifacts
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $PackagePath) {
    $PackagePath = Join-Path $ProjectRoot "dist\MiCochePorDentro"
}
$PackagePath = (Resolve-Path -LiteralPath $PackagePath).Path
$SourceExecutable = Join-Path $PackagePath "MiCochePorDentro.exe"
if (-not (Test-Path -LiteralPath $SourceExecutable)) {
    throw "No se encontró el ejecutable: $SourceExecutable"
}

$SmokeRoot = Join-Path ([System.IO.Path]::GetTempPath()) "MiCochePorDentroTest-$([guid]::NewGuid().ToString('N'))"
$CopiedPackage = Join-Path $SmokeRoot "MiCochePorDentro"
$SmokeHome = Join-Path $SmokeRoot "profile"
$RuntimeFile = Join-Path $SmokeHome "runtime\desktop.json"
$LogFile = Join-Path $SmokeHome "logs\app.log"
New-Item -ItemType Directory -Path $SmokeRoot | Out-Null
Copy-Item -LiteralPath $PackagePath -Destination $CopiedPackage -Recurse
$Executable = Join-Path $CopiedPackage "MiCochePorDentro.exe"

$PreviousHome = $env:MICOCHE_HOME
$PreviousPort = $env:MICOCHE_PORT
$PortBlocker = [System.Net.Sockets.TcpListener]::new(
    [System.Net.IPAddress]::Loopback,
    0
)
$PortBlocker.Start()
$BlockedPort = ([System.Net.IPEndPoint]$PortBlocker.LocalEndpoint).Port
try {
    $env:MICOCHE_HOME = $SmokeHome
    $env:MICOCHE_PORT = [string]$BlockedPort
    $Process = Start-Process `
        -FilePath $Executable `
        -ArgumentList "--headless", "--run-seconds", $RunSeconds `
        -WorkingDirectory ([System.IO.Path]::GetTempPath()) `
        -PassThru
}
finally {
    if ($null -eq $PreviousHome) {
        Remove-Item Env:\MICOCHE_HOME -ErrorAction SilentlyContinue
    }
    else {
        $env:MICOCHE_HOME = $PreviousHome
    }
    if ($null -eq $PreviousPort) {
        Remove-Item Env:\MICOCHE_PORT -ErrorAction SilentlyContinue
    }
    else {
        $env:MICOCHE_PORT = $PreviousPort
    }
}

$Deadline = (Get-Date).AddSeconds(45)
while (-not (Test-Path -LiteralPath $RuntimeFile)) {
    if ($Process.HasExited) {
        throw "El ejecutable terminó antes de publicar su estado. Revisa $LogFile"
    }
    if ((Get-Date) -gt $Deadline) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
        throw "Timeout esperando el arranque del ejecutable. Revisa $LogFile"
    }
    Start-Sleep -Milliseconds 200
}

$Runtime = Get-Content -Raw -LiteralPath $RuntimeFile | ConvertFrom-Json
$PortBlocker.Stop()
if ($Runtime.port -eq $BlockedPort) {
    throw "El ejecutable intentó reutilizar el puerto configurado que estaba ocupado."
}
$BaseUrl = $Runtime.url
$Health = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 5
$Status = Invoke-RestMethod -Uri "$BaseUrl/api/status" -TimeoutSec 5
$Vehicles = Invoke-RestMethod -Uri "$BaseUrl/api/vehicles" -TimeoutSec 5
$Dashboard = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/" -TimeoutSec 5

if ($Health.status -ne "healthy") {
    throw "Respuesta /health no válida."
}
if ($Status.status -ne "online") {
    throw "Respuesta /api/status no válida."
}
if ($Dashboard.StatusCode -ne 200 -or $Dashboard.Content -notmatch "<html") {
    throw "El dashboard no devolvió HTML válido."
}
$AssetMatches = [regex]::Matches($Dashboard.Content, '(?:src|href)="(?<path>/_next/[^"]+)"')
if ($AssetMatches.Count -eq 0) {
    throw "No se encontró ningún recurso estático de Next.js en el dashboard."
}
$AssetPaths = @(
    $AssetMatches |
        ForEach-Object { $_.Groups["path"].Value } |
        Sort-Object -Unique
)
foreach ($AssetPath in $AssetPaths) {
    $Asset = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl$AssetPath" -TimeoutSec 5
    if ($Asset.StatusCode -ne 200) {
        throw "El recurso $AssetPath devolvió HTTP $($Asset.StatusCode)."
    }
}

$PreviousHome = $env:MICOCHE_HOME
try {
    $env:MICOCHE_HOME = $SmokeHome
    $SecondInstance = Start-Process `
        -FilePath $Executable `
        -ArgumentList "--headless", "--run-seconds", "2" `
        -WorkingDirectory ([System.IO.Path]::GetTempPath()) `
        -PassThru
}
finally {
    if ($null -eq $PreviousHome) {
        Remove-Item Env:\MICOCHE_HOME -ErrorAction SilentlyContinue
    }
    else {
        $env:MICOCHE_HOME = $PreviousHome
    }
}
Wait-Process -Id $SecondInstance.Id -Timeout 10
$SecondInstance.Refresh()
if ($SecondInstance.ExitCode -ne 2) {
    throw "La segunda instancia terminó con código $($SecondInstance.ExitCode), se esperaba 2."
}

Wait-Process -Id $Process.Id -Timeout ($RunSeconds + 20)
$Process.Refresh()
if ($Process.ExitCode -ne 0) {
    throw "El ejecutable terminó con código $($Process.ExitCode)."
}
Start-Sleep -Seconds 1

$Listener = Get-NetTCPConnection -State Listen -LocalPort $Runtime.port -ErrorAction SilentlyContinue
$Orphans = Get-CimInstance Win32_Process | Where-Object {
    $_.ExecutablePath -and $_.ExecutablePath.StartsWith($CopiedPackage, [System.StringComparison]::OrdinalIgnoreCase)
}
if ($Listener) {
    throw "El puerto $($Runtime.port) sigue abierto tras el cierre."
}
if ($Orphans) {
    throw "Quedaron procesos del paquete tras el cierre."
}
if (-not (Test-Path -LiteralPath $LogFile)) {
    throw "No se generó el log persistente."
}
$LogContent = Get-Content -Raw -LiteralPath $LogFile
if ($LogContent -cmatch "(?m)^\S+\s+\S+\s+(ERROR|CRITICAL)\s|Traceback") {
    throw "El log contiene errores: $LogFile"
}

[pscustomobject]@{
    Result = "PASS"
    Executable = $Executable
    WorkingDirectory = [System.IO.Path]::GetTempPath()
    Port = $Runtime.port
    Health = $Health.status
    ApiStatus = $Status.status
    VehicleCount = @($Vehicles).Count
    DashboardStatus = $Dashboard.StatusCode
    StaticAssetCount = $AssetPaths.Count
    OccupiedPort = $BlockedPort
    SelectedPort = $Runtime.port
    SecondInstanceExitCode = $SecondInstance.ExitCode
    ExitCode = $Process.ExitCode
    OrphanCount = @($Orphans).Count
    Log = $LogFile
} | Format-List

if (-not $KeepArtifacts) {
    $ResolvedSmokeRoot = (Resolve-Path -LiteralPath $SmokeRoot).Path
    $ResolvedTempRoot = (Resolve-Path -LiteralPath ([System.IO.Path]::GetTempPath())).Path
    if (-not $ResolvedSmokeRoot.StartsWith($ResolvedTempRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Se rechazó limpiar una ruta fuera del directorio temporal."
    }
    Remove-Item -LiteralPath $ResolvedSmokeRoot -Recurse -Force
}
