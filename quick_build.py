#!/usr/bin/env python3
"""
Simple build test for ImageViewer Pro
"""

import subprocess
import sys
import os
from pathlib import Path

def test_app():
    """Test the application without GUI"""
    print("🧪 Testing ImageViewer Pro...")
    
    try:
        # Test imports
        import PyQt5
        print("✅ PyQt5 imported successfully")
        
        import PIL
        print("✅ Pillow imported successfully")
        
        import matplotlib
        print("✅ matplotlib imported successfully")
        
        print("✅ All dependencies available!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def quick_build():
    """Build executable with simpler settings"""
    print("🔨 Building ImageViewer Pro (quick build)...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name=ImageViewerPro",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=os.getcwd(), check=True, 
                              capture_output=True, text=True, timeout=300)
        
        print("✅ Build completed!")
        print(result.stdout)
        
        # Check if exe was created
        exe_path = Path("dist/ImageViewerPro.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable: {exe_path} ({size_mb:.1f} MB)")
            return True
        else:
            print("❌ Executable not found")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Build timeout - trying directory build instead")
        return directory_build()
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def directory_build():
    """Build as directory instead of single file"""
    print("🔨 Building ImageViewer Pro (directory build)...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--windowed",
        "--name=ImageViewerPro",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=os.getcwd(), check=True, 
                              capture_output=True, text=True, timeout=300)
        
        print("✅ Directory build completed!")
        
        # Check if exe was created
        exe_path = Path("dist/ImageViewerPro/ImageViewerPro.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable: {exe_path} ({size_mb:.1f} MB)")
            return True
        else:
            print("❌ Executable not found")
            return False
            
    except Exception as e:
        print(f"❌ Directory build error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ImageViewer Pro Quick Build Test")
    print("=" * 40)
    
    # Test dependencies
    if not test_app():
        print("❌ Dependency test failed")
        sys.exit(1)
    
    # Try quick build
    if not quick_build():
        print("❌ Build failed")
        sys.exit(1)
    
    print("🎉 Build successful!")
