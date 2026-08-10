[CmdletBinding()]
param(
    [switch]$SkipFrontend,
    [switch]$SkipTests,
    [switch]$SkipPyInstaller,
    [switch]$SkipSmokeTest
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VirtualEnvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Python = $VirtualEnvPython
$Dashboard = Join-Path $ProjectRoot "dashboard"
$Spec = Join-Path $ProjectRoot "MiCochePorDentro.spec"

if (-not (Test-Path -LiteralPath $Python)) {
    $SystemPython = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $SystemPython) {
        throw "No se encontró Python 3.11 para compilar."
    }
    $Python = $SystemPython.Source
}
& $Python -c "import sys; assert sys.version_info[:2] == (3, 11) and sys.maxsize > 2**32"
if ($LASTEXITCODE -ne 0) {
    throw "La compilación requiere Python 3.11 de 64 bits."
}

Push-Location $ProjectRoot
try {
    if (-not $SkipFrontend) {
        Push-Location $Dashboard
        try {
            & npm.cmd audit --audit-level=high
            if ($LASTEXITCODE -ne 0) {
                throw "La auditoria de dependencias npm detecto vulnerabilidades de nivel alto o critico."
            }
            & npm.cmd run typecheck
            if ($LASTEXITCODE -ne 0) {
                throw "La comprobacion de tipos de la interfaz fallo."
            }
            & npm.cmd run i18n:check
            if ($LASTEXITCODE -ne 0) {
                throw "La comprobacion de traducciones fallo."
            }
            & npm.cmd run build
            if ($LASTEXITCODE -ne 0) {
                throw "Falló la exportación estática de Next.js."
            }
        }
        finally {
            Pop-Location
        }
    }

    $DashboardIndex = Join-Path $Dashboard "out\index.html"
    if (-not (Test-Path -LiteralPath $DashboardIndex)) {
        throw "Falta dashboard\out\index.html."
    }

    if (-not $SkipTests) {
        & $Python -m pytest -q
        if ($LASTEXITCODE -ne 0) {
            throw "La suite de pruebas falló; no se generará el paquete."
        }
    }

    if (-not $SkipPyInstaller) {
        $ExistingExecutable = Join-Path $ProjectRoot "dist\MiCochePorDentro\MiCochePorDentro.exe"
        $RunningPackage = @(
            Get-CimInstance Win32_Process -Filter "Name = 'MiCochePorDentro.exe'" -ErrorAction SilentlyContinue |
                Where-Object {
                    $_.ExecutablePath -and
                    $_.ExecutablePath.Equals($ExistingExecutable, [System.StringComparison]::OrdinalIgnoreCase)
                }
        )
        if ($RunningPackage.Count) {
            throw "Cierra Mi Coche por Dentro antes de compilar; el ejecutable público está en uso."
        }
        & $Python -m PyInstaller --noconfirm --clean --distpath dist --workpath build $Spec
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller finalizó con error."
        }
    }

    $Executable = Join-Path $ProjectRoot "dist\MiCochePorDentro\MiCochePorDentro.exe"
    if (-not (Test-Path -LiteralPath $Executable)) {
        throw "PyInstaller no creó el ejecutable esperado: $Executable"
    }

    $PackageRoot = Split-Path -Parent $Executable
    $PackageScripts = Join-Path $PackageRoot "scripts"
    New-Item -ItemType Directory -Path $PackageScripts -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "Crear_Acceso_Directo.bat") -Destination $PackageRoot -Force
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "scripts\create_desktop_shortcut.ps1") -Destination $PackageScripts -Force
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "LICENSE") -Destination $PackageRoot -Force
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") -Destination $PackageRoot -Force
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "docs\INSTALACION.md") -Destination (Join-Path $PackageRoot "INSTALACION.md") -Force

    & (Join-Path $PSScriptRoot "verify_public_release.ps1") -PackagePath $PackageRoot
    if ($LASTEXITCODE -ne 0) {
        throw "El paquete contiene archivos no aptos para publicación."
    }

    if (-not $SkipSmokeTest) {
        & (Join-Path $PSScriptRoot "smoke_test_windows.ps1") -PackagePath $PackageRoot -RunSeconds 8
        if ($LASTEXITCODE -ne 0) {
            throw "El ejecutable no superó la prueba de arranque limpio."
        }
    }

    $Version = (& $Python -c "from app_paths import APP_VERSION; print(APP_VERSION)").Trim()
    if ($LASTEXITCODE -ne 0 -or -not $Version) {
        throw "No se pudo determinar la version del paquete."
    }
    $ReleaseZip = Join-Path $ProjectRoot "dist\MiCochePorDentro-$Version-win-x64.zip"
    Compress-Archive -LiteralPath $PackageRoot -DestinationPath $ReleaseZip -CompressionLevel Optimal -Force
    $Hash = (Get-FileHash -LiteralPath $ReleaseZip -Algorithm SHA256).Hash.ToLowerInvariant()
    $HashFile = "$ReleaseZip.sha256"
    "$Hash  $(Split-Path -Leaf $ReleaseZip)" | Set-Content -LiteralPath $HashFile -Encoding ascii

    Write-Host "Paquete creado: $(Split-Path -Parent $Executable)"
    Write-Host "ZIP de publicacion: $ReleaseZip"
    Write-Host "SHA-256: $Hash"
}
finally {
    Pop-Location
}
