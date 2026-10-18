# EasyDP Local PII Scanner — One-Line PowerShell Installer for Windows
# https://easydp.in
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  EasyDP Local PII Scanner — Windows Installer" -ForegroundColor Cyan
Write-Host "  Enterprise-Grade, 100% Offline DPDP Compliance Scanner" -ForegroundColor White
Write-Host "  https://easydp.in" -ForegroundColor DarkGray
Write-Host "============================================================" -ForegroundColor Cyan

$InstallDir = "$env:LOCALAPPDATA\EasyDP\bin"
if (!(Test-Path -Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

$ExePath = Join-Path $InstallDir "easydp-scan.exe"
$BinaryUrl = "https://github.com/easydp-in/pii-scanner/releases/latest/download/pii-scanner-windows-amd64.exe"

try {
    Write-Host "=> Downloading standalone executable..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $BinaryUrl -OutFile $ExePath -UseBasicParsing
    
    # Add to User PATH if not already present
    $UserPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
    if ($UserPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$UserPath;$InstallDir", [EnvironmentVariableTarget]::User)
        $env:Path += ";$InstallDir"
    }

    Write-Host "`n============================================================" -ForegroundColor Green
    Write-Host "  Installation Complete!" -ForegroundColor Green
    Write-Host "  Run: easydp-scan scan C:\Users\YourName\Documents" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Green
} catch {
    Write-Warning "Direct binary download failed. Trying Python pip fallback..."
    if (Get-Command python -ErrorAction SilentlyContinue) {
        python -m pip install --upgrade easydp-pii-scanner
    } else {
        Write-Error "Failed to install EasyDP Local PII Scanner. Please install Python or download manually from https://github.com/easydp-in/pii-scanner/releases"
    }
}
