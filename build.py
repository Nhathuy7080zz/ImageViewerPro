#!/usr/bin/env python3
"""
Simple build script for ImageViewer Pro
Creates an executable using PyInstaller with optimized settings
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Build ImageViewer Pro executable"""
    print("🔨 Building ImageViewer Pro v2.1...")
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build command
    build_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name", "ImageViewerPro_v2.1",
        "--icon", "icon.ico" if Path("icon.ico").exists() else "",
        "--clean",
        "main.py"
    ]
    
    # Remove empty icon parameter if no icon file
    build_cmd = [cmd for cmd in build_cmd if cmd]
    
    print(f"🚀 Running: {' '.join(build_cmd)}")
    
    try:
        result = subprocess.run(build_cmd, check=True)
        print("✅ Build completed successfully!")
        print("📁 Executable created in 'dist' directory")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
