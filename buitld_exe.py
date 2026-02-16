"""
PyInstaller Build Script
This script creates a standalone Windows .exe file

USAGE:
1. Install PyInstaller: pip install pyinstaller
2. Run this script: python build_exe.py
3. Find the .exe in the 'dist' folder

The resulting .exe will work on any Windows computer without Python installed!
"""

import os
import sys
import subprocess

def build_executable():
    """Build standalone executable using PyInstaller"""
    
    print("=" * 60)
    print("CFDI Renamer - Executable Builder")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller is installed")
    except ImportError:
        print("✗ PyInstaller not found")
        print()
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed successfully")
    
    print()
    print("Building executable...")
    print("This may take a few minutes...")
    print()
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=CFDI_Renamer",         # Output name
        "--icon=NONE",                  # No custom icon (you can add one later)
        "--clean",                      # Clean build
        "cfdi_renamer.py"              # Source file
    ]
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 60)
        print("✓ SUCCESS!")
        print("=" * 60)
        print()
        print("Your executable is ready:")
        print("  📁 Location: dist/CFDI_Renamer.exe")
        print()
        print("You can now:")
        print("  1. Double-click CFDI_Renamer.exe to run it")
        print("  2. Copy it to any Windows computer (no Python needed!)")
        print("  3. Share it with your team")
        print()
        print("NOTE: First run may take a few seconds to extract files")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ BUILD FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Try running manually:")
        print(f"  {' '.join(cmd)}")
        print()
        return False
    
    return True

if __name__ == "__main__":
    success = build_executable()
    
    if not success:
        input("Press Enter to close...")
        sys.exit(1)
    
    input("Press Enter to close...")