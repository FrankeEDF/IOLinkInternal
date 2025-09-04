#!/usr/bin/env python3
"""
Build script to create executable for RFID Modbus Test GUI
Uses PyInstaller to create a standalone Windows executable
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller version {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("✗ PyInstaller not found")
        return False

def install_pyinstaller():
    """Install PyInstaller using pip"""
    print("Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install PyInstaller")
        return False

def build_exe():
    """Build the executable using PyInstaller"""
    print("\nBuilding RFID Modbus Test GUI executable...")

    # PyInstaller command with options
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                    # No console window (GUI application)
        "--name", "RfidModbusTestGUI",  # Name of the executable
        "--icon", "NONE",                # No icon (can be added if available)
        "--clean",                       # Clean cache before building
        "--noconfirm",                   # Overwrite output without confirmation
        "--add-data", "requirements.txt;.",  # Include requirements.txt if needed
        "RfidModbusTestGUI.py"          # Main Python script
    ]

    # Additional options for better compatibility
    cmd.extend([
        "--hidden-import", "pymodbus.client.sync",
        "--hidden-import", "pymodbus.constants",
        "--hidden-import", "pymodbus.payload",
        "--hidden-import", "serial.tools.list_ports",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.scrolledtext",
    ])

    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Build completed successfully!")

            # Check if exe was created
            exe_path = os.path.join("dist", "RfidModbusTestGUI.exe")
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Convert to MB
                print(f"\n✓ Executable created: {exe_path}")
                print(f"  File size: {file_size:.2f} MB")

                # Copy to current directory for easy access
                current_dir_exe = "RfidModbusTestGUI.exe"
                shutil.copy2(exe_path, current_dir_exe)
                print(f"  Copied to: {current_dir_exe}")

                return True
            else:
                print("✗ Executable not found in dist folder")
                return False
        else:
            print("✗ Build failed!")
            print("Error output:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def install_dependencies():
    """Install required dependencies from requirements.txt"""
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def main():
    """Main build process"""
    print("=" * 60)
    print("RFID Modbus Test GUI - Executable Builder")
    print("=" * 60)

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")

    # Step 1: Install dependencies
    print("\n[Step 1] Checking dependencies...")
    if not install_dependencies():
        print("Warning: Some dependencies might be missing")

    # Step 2: Check/Install PyInstaller
    print("\n[Step 2] Checking PyInstaller...")
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("\nFailed to install PyInstaller. Please install it manually:")
            print("  pip install pyinstaller")
            return 1

    # Step 3: Build executable
    print("\n[Step 3] Building executable...")
    if build_exe():
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print("\nThe executable 'RfidModbusTestGUI.exe' has been created.")
        print("You can now run it without Python installed.")
        print("\nNote: Windows Defender might flag the exe as suspicious")
        print("on first run. This is normal for PyInstaller executables.")
        return 0
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        print("\nPlease check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
