<#
.SYNOPSIS
    NETSpeed Installer for Windows (by RipoN)
    Installs NETSpeed into LocalAppData, creates Desktop & Start Menu shortcuts.
#>

param(
    [switch]$Uninstall,
    [switch]$NoLaunch
)

$AppName = "NETSpeed"
$Author = "RipoN"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\$AppName"
$ExeTarget = Join-Path $InstallDir "$AppName.exe"
$SourceExe = Join-Path $PSScriptRoot "NETSpeed.exe"

# If running from repo root or dist
if (-not (Test-Path $SourceExe)) {
    $SourceExe = Join-Path $PSScriptRoot "dist\NETSpeed.exe"
}

$WshShell = New-Object -ComObject WScript.Shell

# Desktop Shortcut Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$DesktopShortcut = Join-Path $DesktopPath "$AppName.lnk"

# Start Menu Shortcut Path
$StartMenuPath = [Environment]::GetFolderPath("Programs")
$StartMenuShortcut = Join-Path $StartMenuPath "$AppName.lnk"

if ($Uninstall) {
    Write-Host "Uninstalling $AppName by $Author..." -ForegroundColor Yellow

    # Stop any running instances
    Get-Process $AppName -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

    if (Test-Path $DesktopShortcut) { Remove-Item $DesktopShortcut -Force }
    if (Test-Path $StartMenuShortcut) { Remove-Item $StartMenuShortcut -Force }
    if (Test-Path $InstallDir) { Remove-Item $InstallDir -Recurse -Force }

    Write-Host "$AppName successfully uninstalled." -ForegroundColor Green
    exit 0
}

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Installing $AppName by $Author" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

if (-not (Test-Path $SourceExe)) {
    Write-Host "Error: Could not locate NETSpeed.exe in $PSScriptRoot or $PSScriptRoot\dist." -ForegroundColor Red
    exit 1
}

# 1. Stop existing process if running
Get-Process $AppName -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Create destination folder
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# 3. Copy files
Write-Host "[1/3] Copying files to $InstallDir..." -ForegroundColor Gray
Copy-Item -Path $SourceExe -Destination $ExeTarget -Force

$SourceIco = Join-Path $PSScriptRoot "NetSpeed.ico"
if (-not (Test-Path $SourceIco)) { $SourceIco = Join-Path (Split-Path $PSScriptRoot) "NetSpeed.ico" }
if (Test-Path $SourceIco) {
    Copy-Item -Path $SourceIco -Destination (Join-Path $InstallDir "NetSpeed.ico") -Force
}

$SourcePng = Join-Path $PSScriptRoot "NetSpeed.png"
if (-not (Test-Path $SourcePng)) { $SourcePng = Join-Path (Split-Path $PSScriptRoot) "NetSpeed.png" }
if (Test-Path $SourcePng) {
    Copy-Item -Path $SourcePng -Destination (Join-Path $InstallDir "NetSpeed.png") -Force
}

# 4. Create Desktop & Start Menu Shortcuts
Write-Host "[2/3] Creating Start Menu and Desktop shortcuts..." -ForegroundColor Gray
$TargetIco = Join-Path $InstallDir "NetSpeed.ico"
$IconLocation = if (Test-Path $TargetIco) { "$TargetIco,0" } else { "$ExeTarget,0" }

# Desktop
$Shortcut = $WshShell.CreateShortcut($DesktopShortcut)
$Shortcut.TargetPath = $ExeTarget
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "NETSpeed Internet Speed Monitor by RipoN"
$Shortcut.IconLocation = $IconLocation
$Shortcut.Save()

# Start Menu
$ShortcutSM = $WshShell.CreateShortcut($StartMenuShortcut)
$ShortcutSM.TargetPath = $ExeTarget
$ShortcutSM.WorkingDirectory = $InstallDir
$ShortcutSM.Description = "NETSpeed Internet Speed Monitor by RipoN"
$ShortcutSM.IconLocation = $IconLocation
$ShortcutSM.Save()

Write-Host "[3/3] Finalizing installation..." -ForegroundColor Gray
Write-Host ""
Write-Host "NETSpeed successfully installed to: $InstallDir" -ForegroundColor Green
Write-Host "Desktop and Start Menu shortcuts created." -ForegroundColor Green

if (-not $NoLaunch) {
    Write-Host "Launching $AppName..." -ForegroundColor Cyan
    Start-Process $ExeTarget
}

Write-Host "=========================================" -ForegroundColor Cyan
