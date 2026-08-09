[CmdletBinding()]
param(
    [string]$ProjectRoot = "",
    [string]$DesktopPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = $ProjectRoot.Trim().Trim('"')
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

if (-not $DesktopPath) {
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
}
if (-not $DesktopPath) {
    throw "Windows no devolvio la ruta del escritorio."
}
New-Item -ItemType Directory -Path $DesktopPath -Force | Out-Null
$DesktopPath = (Resolve-Path -LiteralPath $DesktopPath).Path

$PackagedExecutable = Join-Path $ProjectRoot "MiCochePorDentro.exe"
$BuiltExecutable = Join-Path $ProjectRoot "dist\MiCochePorDentro\MiCochePorDentro.exe"
$SourceLauncher = Join-Path $ProjectRoot "Iniciar_MiCochePorDentro.vbs"

$Arguments = ""
if (Test-Path -LiteralPath $PackagedExecutable) {
    $Target = $PackagedExecutable
    $WorkingDirectory = $ProjectRoot
    $Icon = "$PackagedExecutable,0"
}
elseif (Test-Path -LiteralPath $BuiltExecutable) {
    $Target = $BuiltExecutable
    $WorkingDirectory = Split-Path -Parent $BuiltExecutable
    $Icon = "$BuiltExecutable,0"
}
elseif (Test-Path -LiteralPath $SourceLauncher) {
    $Target = Join-Path $env:WINDIR "System32\wscript.exe"
    $Arguments = '"' + $SourceLauncher + '"'
    $WorkingDirectory = $ProjectRoot
    $Icon = "$Target,0"
}
else {
    throw "No se encontro MiCochePorDentro.exe ni Iniciar_MiCochePorDentro.vbs en $ProjectRoot."
}

$ShortcutPath = Join-Path $DesktopPath "Mi Coche por Dentro.lnk"
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $Target
$Shortcut.Arguments = $Arguments
$Shortcut.WorkingDirectory = $WorkingDirectory
$Shortcut.IconLocation = $Icon
$Shortcut.Description = "Abrir Mi Coche por Dentro"
$Shortcut.Save()

Write-Host "Acceso directo creado: $ShortcutPath" -ForegroundColor Green
