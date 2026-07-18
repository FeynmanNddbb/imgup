param(
    [string]$Version = "1.0.2"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReleaseDir = Join-Path $ProjectRoot "release"
$BuildDistDir = Join-Path $ProjectRoot "build\release-dist"
$BuildWorkDir = Join-Path $ProjectRoot "build\release-work"
$PackageDir = Join-Path $ProjectRoot "build\release-package\imgup-windows-x64"
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

New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
if (Test-Path $PackageDir) {
    Remove-Item -LiteralPath $PackageDir -Recurse -Force
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
