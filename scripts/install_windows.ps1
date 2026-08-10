[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$SkipShortcut
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Dashboard = Join-Path $ProjectRoot "dashboard"

function Show-MissingRequirement {
    param([string]$Name, [string]$Command)
    Write-Host ""
    Write-Host "Falta $Name." -ForegroundColor Yellow
    Write-Host "Instalalo desde PowerShell con:" -ForegroundColor Yellow
    Write-Host "  $Command" -ForegroundColor Cyan
    Write-Host "Despues cierra y vuelve a abrir la carpeta y ejecuta otra vez Instalar_MiCochePorDentro.bat."
}

$Missing = $false
$ExistingPythonReady = $false
if (Test-Path -LiteralPath $Python) {
    & $Python -c "import sys; assert sys.version_info[:2] == (3, 11) and sys.maxsize > 2**32"
    $ExistingPythonReady = $LASTEXITCODE -eq 0
}

if (-not $ExistingPythonReady) {
    $PyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if (-not $PyLauncher) {
        Show-MissingRequirement "Python 3.11 de 64 bits" "winget install -e --id Python.Python.3.11"
        $Missing = $true
    }
    else {
        & py.exe -3.11 -c "import sys; assert sys.maxsize > 2**32"
        if ($LASTEXITCODE -ne 0) {
            Show-MissingRequirement "Python 3.11 de 64 bits" "winget install -e --id Python.Python.3.11"
            $Missing = $true
        }
    }
}

$NodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
$NpmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $NodeCommand -or -not $NpmCommand) {
    Show-MissingRequirement "Node.js LTS y npm" "winget install -e --id OpenJS.NodeJS.LTS"
    $Missing = $true
}
else {
    $NodeMajor = [int]((& node.exe -p "process.versions.node.split('.')[0]").Trim())
    if ($NodeMajor -lt 20) {
        Show-MissingRequirement "Node.js 20 o posterior" "winget upgrade -e --id OpenJS.NodeJS.LTS"
        $Missing = $true
    }
}

if ($Missing) {
    throw "Instala los requisitos indicados antes de continuar."
}

if ($CheckOnly) {
    Write-Host "Python 3.11, Node.js y npm estan disponibles." -ForegroundColor Green
    return
}

Push-Location $ProjectRoot
try {
    if (-not (Test-Path -LiteralPath $Python)) {
        Write-Host "Creando el entorno de Python..."
        & py.exe -3.11 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno de Python." }
    }

    Write-Host "Instalando dependencias de Python..."
    & $Python -m pip install --upgrade pip setuptools wheel
    if ($LASTEXITCODE -ne 0) { throw "No se pudieron actualizar pip, setuptools y wheel." }
    & $Python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias de Python." }

    Write-Host "Preparando la interfaz..."
    Push-Location $Dashboard
    try {
        & npm.cmd ci
        if ($LASTEXITCODE -ne 0) { throw "npm ci termino con error." }
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw "La compilacion de la interfaz termino con error." }
    }
    finally {
        Pop-Location
    }

    $EnvironmentFile = Join-Path $ProjectRoot ".env"
    if (-not (Test-Path -LiteralPath $EnvironmentFile)) {
        Copy-Item -LiteralPath (Join-Path $ProjectRoot ".env.example") -Destination $EnvironmentFile
    }

    if (-not $SkipShortcut) {
        & (Join-Path $PSScriptRoot "create_desktop_shortcut.ps1") -ProjectRoot $ProjectRoot
    }

    Write-Host ""
    Write-Host "Mi Coche por Dentro esta preparado." -ForegroundColor Green
    Write-Host "Puedes abrirlo desde el acceso directo del escritorio o desde Iniciar_App.bat."
}
finally {
    Pop-Location
}
