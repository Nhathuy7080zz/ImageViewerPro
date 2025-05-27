#!/usr/bin/env python3
"""
Simple build script for ImageViewer Pro
"""

import subprocess
import sys
import os

def main():
    print("🔧 Building ImageViewer Pro...")
    
    # Simple PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=ImageViewerPro",
        "main.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print("📁 Executable created in 'dist' folder")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

if __name__ == "__main__":
    main()
