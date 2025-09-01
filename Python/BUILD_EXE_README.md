# Building RFID Modbus Test GUI as Windows Executable

This guide explains how to create a standalone Windows executable (.exe) from the RFID Modbus Test GUI Python application.

## Prerequisites

- **Python 3.7 or later** installed on Windows
- **pip** package manager (comes with Python)

## Build Methods

### Method 1: Using PowerShell Script (Recommended)

1. Open PowerShell as Administrator
2. Navigate to the Python directory:
   ```powershell
   cd C:\git\Schlegel\IOLink\Firmware\Python
   ```
3. Enable script execution (if needed):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. Run the build script:
   ```powershell
   .\build_exe.ps1
   ```

### Method 2: Using Batch File

1. Open Command Prompt
2. Navigate to the Python directory:
   ```cmd
   cd C:\git\Schlegel\IOLink\Firmware\Python
   ```
3. Run the batch file:
   ```cmd
   build_exe.bat
   ```

### Method 3: Manual Build

1. Open Command Prompt or PowerShell
2. Navigate to the Python directory
3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```
4. Build the executable:
   ```cmd
   pyinstaller --onefile --windowed --name RfidModbusTestGUI --clean --noconfirm RfidModbusTestGUI.py
   ```

## Output

After successful build:
- The executable will be located in: `dist\RfidModbusTestGUI.exe`
- File size: Approximately 15-25 MB
- This is a standalone executable that can run on any Windows system without Python installed

## Troubleshooting

### Issue: "Python is not recognized"
- **Solution**: Install Python from [python.org](https://www.python.org/) and ensure "Add Python to PATH" is checked during installation

### Issue: "pip is not recognized"
- **Solution**: Reinstall Python with pip included, or run:
  ```cmd
  python -m ensurepip --upgrade
  ```

### Issue: Windows Defender blocks the executable
- **Solution**: This is common with PyInstaller executables. Add an exception in Windows Defender or click "More info" → "Run anyway"

### Issue: "Failed to execute script" error when running the exe
- **Solution**: Ensure all dependencies are installed before building:
  ```cmd
  pip install pymodbus pyserial
  ```

### Issue: COM ports not detected in the executable
- **Solution**: Run the executable as Administrator

## Features of the Executable

The standalone executable includes:
- Full RFID Modbus Test GUI functionality
- All Python dependencies bundled
- No Python installation required on target machine
- Windows GUI application (no console window)

## Distribution

To distribute the application:
1. Copy `dist\RfidModbusTestGUI.exe` to the target machine
2. No additional files or installation needed
3. Run the executable directly

## Notes

- The executable is larger than the Python script because it includes the Python interpreter and all dependencies
- First startup might be slower as Windows Defender scans the file
- The executable is optimized for Windows 10/11 x64 systems