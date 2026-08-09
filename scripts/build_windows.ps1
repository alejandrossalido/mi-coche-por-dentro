[CmdletBinding()]
param(
    [switch]$SkipFrontend,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Dashboard = Join-Path $ProjectRoot "dashboard"
$Spec = Join-Path $ProjectRoot "MiCochePorDentro.spec"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No se encontró el entorno de compilación: $Python"
}

Push-Location $ProjectRoot
try {
    if (-not $SkipFrontend) {
        Push-Location $Dashboard
        try {
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

    & $Python -m PyInstaller --noconfirm --clean --distpath dist --workpath build $Spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller finalizó con error."
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

    Write-Host "Paquete creado: $(Split-Path -Parent $Executable)"
}
finally {
    Pop-Location
}
