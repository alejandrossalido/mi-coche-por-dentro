[CmdletBinding()]
param(
    [string]$PackagePath = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$ForbiddenExtensions = @(
    ".db",
    ".sqlite",
    ".sqlite3",
    ".parquet",
    ".log",
    ".stdout",
    ".stderr"
)

function Test-ForbiddenPath {
    param([string]$RelativePath)

    $Normalized = $RelativePath.Replace("\", "/")
    if ($Normalized.StartsWith("_internal/pyarrow/tests/")) {
        return $false
    }
    $Leaf = [System.IO.Path]::GetFileName($Normalized)
    $Extension = [System.IO.Path]::GetExtension($Leaf).ToLowerInvariant()
    if ($ForbiddenExtensions -contains $Extension) {
        return $true
    }
    if ($Leaf -eq ".env" -or ($Leaf.StartsWith(".env.") -and $Leaf -ne ".env.example")) {
        return $true
    }
    return $false
}

$Git = Get-Command git.exe -ErrorAction SilentlyContinue
if ($Git -and (Test-Path -LiteralPath (Join-Path $ProjectRoot ".git"))) {
    $TrackedFiles = @(& $Git.Source -C $ProjectRoot -c core.quotepath=false ls-files)
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo obtener la lista de archivos versionados."
    }
    $ForbiddenTracked = @($TrackedFiles | Where-Object { Test-ForbiddenPath $_ })
    if ($ForbiddenTracked.Count) {
        throw "Git contiene datos locales prohibidos: $($ForbiddenTracked -join ', ')"
    }
}

if ($PackagePath) {
    $ResolvedPackage = (Resolve-Path -LiteralPath $PackagePath).Path
    $RequiredFiles = @(
        "MiCochePorDentro.exe",
        "LICENSE",
        "README.md",
        "INSTALACION.md",
        "Crear_Acceso_Directo.bat",
        "scripts\create_desktop_shortcut.ps1"
    )
    foreach ($RequiredFile in $RequiredFiles) {
        if (-not (Test-Path -LiteralPath (Join-Path $ResolvedPackage $RequiredFile))) {
            throw "El paquete no incluye $RequiredFile."
        }
    }

    $ForbiddenPackageFiles = @(
        Get-ChildItem -LiteralPath $ResolvedPackage -File -Recurse -Force |
            Where-Object {
                $Relative = $_.FullName.Substring($ResolvedPackage.Length).TrimStart("\", "/")
                Test-ForbiddenPath $Relative
            }
    )
    if ($ForbiddenPackageFiles.Count) {
        $Names = $ForbiddenPackageFiles | ForEach-Object {
            $_.FullName.Substring($ResolvedPackage.Length).TrimStart("\", "/")
        }
        throw "El paquete contiene datos locales prohibidos: $($Names -join ', ')"
    }
}

[pscustomobject]@{
    Result = "PASS"
    Repository = $ProjectRoot
    Package = if ($PackagePath) { (Resolve-Path -LiteralPath $PackagePath).Path } else { "No comprobado" }
    PersonalDataFiles = 0
} | Format-List
