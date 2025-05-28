#!/usr/bin/env python3
"""
Setup script for ImageViewer Pro v2.1
Installs all required dependencies
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages"""
    print("📦 Installing ImageViewer Pro v2.1 dependencies...")
    
    try:
        # Install from requirements.txt
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ All dependencies installed successfully!")
        
        # Test imports
        print("🧪 Testing imports...")
        try:
            import PyQt5
            import PIL
            import matplotlib
            import numpy
            print("✅ All imports successful!")
            
            # Test main application
            print("🧪 Testing application...")
            from main import ImageViewer
            print("✅ ImageViewer Pro ready!")
            
            print("\n🎉 Setup completed successfully!")
            print("💡 Run the application with: python main.py")
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return 1
    
    return 0

def main():
    """Main setup function"""
    print("🖼️ ImageViewer Pro v2.1 Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return 1
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    return install_requirements()

if __name__ == "__main__":
    exit(main())
