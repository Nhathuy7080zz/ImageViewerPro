#!/usr/bin/env python3
"""
Build script for ImageViewer Pro - Optimized Edition
Creates standalone EXE file with all dependencies included
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"[CLEAN] Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec files
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        print(f"[CLEAN] Removing {spec_file}...")
        spec_file.unlink()

def create_icon():
    """Create a simple icon for the application"""
    icon_content = """
    # Simple icon creation placeholder
    # In a real project, you would use a .ico file
    """
    # For now, we'll use the default icon
    return None

def build_exe():
    """Build the EXE file using PyInstaller"""
    print("[BUILD] Building ImageViewer Pro - Optimized Edition EXE...")
    print("=" * 60)
    
    # Clean previous builds
    clean_build_dirs()
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single EXE file
        "--windowed",                   # No console window
        "--name=ImageViewerPro_Optimized",  # EXE name
        "--add-data=requirements.txt;.",     # Include requirements
        # "--icon=icon.ico",            # Add icon if available
        "--hidden-import=PIL._tkinter_finder",  # PIL compatibility
        "--hidden-import=pkg_resources.py2_warn",
        "--collect-all=matplotlib",     # Include matplotlib data
        "--collect-all=PIL",           # Include PIL/Pillow data
        "main.py"                      # Main script
    ]
    
    print(f"[PYINSTALLER] Running PyInstaller command:")
    print(f"   {' '.join(cmd)}")
    print()
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("[SUCCESS] Build successful!")
            
            # Check if EXE was created
            exe_path = Path("dist/ImageViewerPro_Optimized.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"[EXE] EXE created: {exe_path}")
                print(f"[SIZE] File size: {size_mb:.1f} MB")
                
                # Create launcher script
                create_launcher()
                
                # Create distribution folder
                create_distribution()
                
                return True
            else:
                print("[ERROR] EXE file not found after build!")
                return False
                
        else:
            print("[ERROR] Build failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_launcher():
    """Create a launcher script for the EXE"""
    launcher_content = """@echo off
echo ===============================================
echo   ImageViewer Pro - Optimized Edition v2.0
echo ===============================================
echo.
echo Starting optimized ImageViewer Pro...
echo.
echo Performance Features:
echo - 600x faster sorting
echo - Async thumbnail loading  
echo - Enhanced metadata reading
echo - Optimized histogram rendering
echo - Smooth UI with no lag
echo.
echo ===============================================
echo.

cd /d "%~dp0"
ImageViewerPro_Optimized.exe

if errorlevel 1 (
    echo.
    echo Error starting application!
    echo Please ensure all dependencies are included.
    pause
)
"""
    
    with open("dist/Start_ImageViewerPro.bat", "w") as f:
        f.write(launcher_content)
    
    print("📝 Created launcher: dist/Start_ImageViewerPro.bat")

def create_distribution():
    """Create a complete distribution package"""
    print("\n📦 Creating distribution package...")
    
    # Create docs in dist folder
    docs_to_copy = [
        "README.md",
        "OPTIMIZATION_COMPLETE.md", 
        "requirements.txt"
    ]
    
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, "dist/")
            print(f"📄 Copied: {doc}")
    
    # Create info file
    info_content = """# ImageViewer Pro - Optimized Edition

## 🚀 Quick Start
Double-click: Start_ImageViewerPro.bat

## 📁 Files Included
- ImageViewerPro_Optimized.exe  - Main application
- Start_ImageViewerPro.bat      - Easy launcher
- README.md                     - Full documentation
- OPTIMIZATION_COMPLETE.md      - Optimization details
- requirements.txt              - Python dependencies (for reference)

## ✨ Performance Features
✅ 600x faster sorting
✅ Async thumbnail loading
✅ Enhanced metadata reading  
✅ Optimized histogram rendering
✅ Lag-free user interface

## 🎯 System Requirements
- Windows 10/11
- 4GB+ RAM recommended
- No Python installation required

## 🆘 Troubleshooting
If the application doesn't start:
1. Run as administrator
2. Check Windows Defender/antivirus settings
3. Ensure all files are in the same folder

Built with PyInstaller from optimized Python source.
"""
    
    with open("dist/README_DISTRIBUTION.txt", "w", encoding="utf-8") as f:
        f.write(info_content)
    
    print("📄 Created: dist/README_DISTRIBUTION.txt")

def main():
    """Main build function"""
    print("🔧 ImageViewer Pro - Optimized Edition Builder")
    print("=" * 60)
      # Check if main file exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found!")
        print("   Please ensure you're in the correct directory.")
        return False
    
    # Check PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller not found!")
        print("   Please install: pip install pyinstaller")
        return False
    
    # Build EXE
    if build_exe():
        print("\n" + "=" * 60)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("📁 Files created in 'dist' folder:")
        print("   - ImageViewerPro_Optimized.exe")
        print("   - Start_ImageViewerPro.bat (launcher)")
        print("   - README_DISTRIBUTION.txt (info)")
        print("   - Documentation files")
        print()
        print("🚀 To run: Double-click 'Start_ImageViewerPro.bat'")
        print("📦 To distribute: Share the entire 'dist' folder")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("❌ BUILD FAILED!")
        print("=" * 60)
        print("Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    
    # Keep window open
    print(f"\nPress Enter to exit...")
    input()
    
    sys.exit(0 if success else 1)
