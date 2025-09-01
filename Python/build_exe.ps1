# PowerShell script to build RFID Modbus Test GUI executable
# Run this script in PowerShell on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RFID Modbus Test GUI - EXE Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7 or later from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install required packages
Write-Host ""
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some dependencies might not have installed correctly" -ForegroundColor Yellow
}

# Install PyInstaller
Write-Host ""
Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Build the executable
Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow

$buildCommand = @"
pyinstaller --onefile --windowed --name RfidModbusTestGUI --clean --noconfirm `
    --hidden-import pymodbus.client.sync `
    --hidden-import pymodbus.constants `
    --hidden-import pymodbus.payload `
    --hidden-import serial.tools.list_ports `
    --hidden-import tkinter `
    --hidden-import tkinter.ttk `
    --hidden-import tkinter.scrolledtext `
    RfidModbusTestGUI.py
"@

Invoke-Expression $buildCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The executable has been created in:" -ForegroundColor Cyan
    Write-Host "  dist\RfidModbusTestGUI.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "You can now run the program without Python installed." -ForegroundColor Cyan
    
    # Get file size
    if (Test-Path "dist\RfidModbusTestGUI.exe") {
        $fileSize = (Get-Item "dist\RfidModbusTestGUI.exe").Length / 1MB
        Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"