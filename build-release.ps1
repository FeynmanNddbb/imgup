param(
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReleaseDir = Join-Path $ProjectRoot "release"
$PackageDir = Join-Path $ReleaseDir "imgup-windows-x64"
$BuildDistDir = Join-Path $ProjectRoot "build\release-dist"
$BuildWorkDir = Join-Path $ProjectRoot "build\release-work"
$ExeName = "imgup-windows-x64-v$Version.exe"
$ZipName = "imgup-windows-x64-v$Version.zip"

Set-Location $ProjectRoot

python tools/create_icon.py
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create Windows icon."
}

python -m PyInstaller --noconfirm --clean --distpath $BuildDistDir --workpath $BuildWorkDir imgup.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

if (Test-Path $ReleaseDir) {
    $ResolvedRelease = (Resolve-Path $ReleaseDir).Path
    $ResolvedRoot = (Resolve-Path $ProjectRoot).Path
    if (-not $ResolvedRelease.StartsWith($ResolvedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a release directory outside the project."
    }
    Remove-Item -LiteralPath $ReleaseDir -Recurse -Force
}

New-Item -ItemType Directory -Path $PackageDir | Out-Null
$BuiltExe = Join-Path $BuildDistDir "imgup.exe"
Copy-Item $BuiltExe (Join-Path $ReleaseDir $ExeName)
Copy-Item $BuiltExe (Join-Path $PackageDir "imgup.exe")
Copy-Item "WINDOWS_README.txt" $PackageDir
Copy-Item "LICENSE" $PackageDir

Compress-Archive -Path "$PackageDir/*" -DestinationPath (Join-Path $ReleaseDir $ZipName) -CompressionLevel Optimal

$Artifacts = @(
    (Join-Path $ReleaseDir $ExeName),
    (Join-Path $ReleaseDir $ZipName)
)

$Checksums = foreach ($Artifact in $Artifacts) {
    $Hash = Get-FileHash -Algorithm SHA256 -LiteralPath $Artifact
    "{0}  {1}" -f $Hash.Hash.ToLowerInvariant(), (Split-Path -Leaf $Artifact)
}
$Checksums | Set-Content -Path (Join-Path $ReleaseDir "SHA256SUMS.txt") -Encoding ascii

Write-Host "Release artifacts created in $ReleaseDir"
Get-ChildItem $ReleaseDir | Select-Object Name, Length, LastWriteTime
