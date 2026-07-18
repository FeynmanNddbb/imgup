# imgup Windows release packaging

## Build

Run this command from the project root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build-release.ps1 -Version 1.0.2
```

## Output

The script creates release-ready files in `release/`:

- `imgup-windows-x64-v1.0.2.exe`: single-file Windows app for direct GitHub Release downloads
- `imgup-windows-x64-v1.0.2.zip`: zip package with the app, license, and usage notes
- `SHA256SUMS.txt`: SHA-256 checksums for release verification

## Icon

The app icon is generated from `imgup.png` into `imgup.ico`.
PyInstaller embeds `imgup.ico` into the exe and bundles `imgup.png` for the Tk window icon.

## Requirements

```powershell
python -m pip install pyinstaller pillow
```
