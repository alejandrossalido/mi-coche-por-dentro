$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "No se encontró el entorno virtual: $Python"
}

& $Python (Join-Path $ProjectRoot "desktop_launcher.py")
exit $LASTEXITCODE
