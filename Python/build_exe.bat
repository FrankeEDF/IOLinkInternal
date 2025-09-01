@echo off
REM Build script for RFID Modbus Test GUI executable
REM This creates a standalone .exe file that can run without Python

echo ========================================
echo RFID Modbus Test GUI - EXE Builder
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies might not have installed correctly
)

echo.
echo Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Building executable...
pyinstaller --onefile --windowed --name RfidModbusTestGUI --clean --noconfirm ^
    --hidden-import pymodbus.client.sync ^
    --hidden-import pymodbus.constants ^
    --hidden-import pymodbus.payload ^
    --hidden-import serial.tools.list_ports ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.scrolledtext ^
    RfidModbusTestGUI.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo The executable has been created in: dist\RfidModbusTestGUI.exe
echo.
echo You can now run the program without Python installed.
echo.
pause