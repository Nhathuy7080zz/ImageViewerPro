#!/usr/bin/env python3
"""
Build script for ImageViewer Pro
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def create_icon():
    """Create a simple icon file"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon
        size = (256, 256)
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a simple camera-like icon
        # Body
        draw.rectangle([50, 80, 206, 176], fill=(70, 130, 180), outline=(25, 25, 112), width=3)
        
        # Lens
        draw.ellipse([80, 100, 176, 156], fill=(220, 220, 220), outline=(25, 25, 112), width=3)
        draw.ellipse([100, 115, 156, 141], fill=(50, 50, 50))
        
        # Flash
        draw.rectangle([170, 90, 190, 110], fill=(255, 255, 0), outline=(255, 165, 0), width=2)
        
        # Save icon
        image.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print("✅ Created application icon")
        return True
    except Exception as e:
        print(f"⚠️ Could not create icon: {e}")
        return False

def build_exe():
    """Build the executable using PyInstaller"""
    print("🔨 Building ImageViewer Pro executable...")
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create icon
    icon_available = create_icon()
    
    # Prepare build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Create single executable
        "--windowed",                   # Hide console window
        "--name=ImageViewerPro",        # Executable name
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--clean",                      # Clean build
    ]
    
    # Add icon if available
    if icon_available and os.path.exists('icon.ico'):
        cmd.extend(["--icon=icon.ico"])
    
    # Add main script
    cmd.append("main.py")
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            
            # Check if executable was created
            exe_path = Path("dist/ImageViewerPro.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable created: {exe_path}")
                print(f"📏 Size: {size_mb:.1f} MB")
                
                # Create launcher script
                create_launcher()
                
                # Create distribution info
                create_dist_info()
                
                return True
            else:
                print("❌ Executable not found in dist directory")
                return False
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_launcher():
    """Create a batch file launcher"""
    launcher_content = '''@echo off
title ImageViewer Pro
echo Starting ImageViewer Pro...
echo.

REM Check if executable exists
if not exist "ImageViewerPro.exe" (
    echo Error: ImageViewerPro.exe not found!
    echo Please ensure you're running this from the correct directory.
    pause
    exit /b 1
)

REM Run the application
"ImageViewerPro.exe" %*

REM Check exit code
if %ERRORLEVEL% neq 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    pause
)
'''
    
    try:
        with open('dist/Launch_ImageViewerPro.bat', 'w') as f:
            f.write(launcher_content)
        print("✅ Created launcher script: Launch_ImageViewerPro.bat")
    except Exception as e:
        print(f"⚠️ Could not create launcher: {e}")

def create_dist_info():
    """Create distribution information file"""
    dist_info = """ImageViewer Pro v2.0 - Distribution Package
===========================================

📦 Contents:
- ImageViewerPro.exe         : Main application executable
- Launch_ImageViewerPro.bat  : Launcher script (optional)
- README.txt                 : This file

🚀 Quick Start:
1. Double-click ImageViewerPro.exe to run the application
2. Or use Launch_ImageViewerPro.bat for verbose startup

📁 Opening Images:
- Use Ctrl+O to open a single image
- Use Ctrl+Shift+O to open a folder of images
- Drag and drop images onto the application (if supported)

⌨️ Keyboard Shortcuts:
- F11: Toggle fullscreen
- Ctrl+T: Toggle dark/light theme
- Left/Right arrows: Navigate between images
- Ctrl++/-: Zoom in/out
- Ctrl+0: Actual size
- Ctrl+9: Fit to window

🔧 System Requirements:
- Windows 7/8/10/11
- No additional software required (standalone executable)

🐛 Troubleshooting:
- If the application doesn't start, try running Launch_ImageViewerPro.bat
- Check Windows Defender/Antivirus settings if executable is blocked
- Ensure you have appropriate permissions to run the executable

📧 Support:
- Email: nhathuy7080zz@gmail.com
- GitHub: https://github.com/Nhathuy7080zz/ImageViewerPro

Built with PyQt5, Pillow, and matplotlib
© 2024 Phan Nhật Huy
"""
    
    try:
        with open('dist/README.txt', 'w', encoding='utf-8') as f:
            f.write(dist_info)
        print("✅ Created distribution info: README.txt")
    except Exception as e:
        print(f"⚠️ Could not create distribution info: {e}")

def clean_build():
    """Clean build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    # Remove build directories
    for directory in ['build', 'dist', '__pycache__']:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"🗑️ Removed {directory}/")
    
    # Remove spec file
    spec_file = 'ImageViewerPro.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"🗑️ Removed {spec_file}")
    
    # Remove icon file
    if os.path.exists('icon.ico'):
        os.remove('icon.ico')
        print(f"🗑️ Removed icon.ico")
    
    print("✅ Cleanup completed")

def main():
    """Main build function"""
    print("🏗️ ImageViewer Pro Build System")
    print("================================")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        clean_build()
        return
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("❌ main.py not found! Please run this script from the project directory.")
        return
    
    # Build the executable
    success = build_exe()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("📁 Check the 'dist' directory for your executable")
        print("🚀 Run ImageViewerPro.exe to start the application")
    else:
        print("\n❌ Build failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
