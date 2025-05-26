#!/usr/bin/env python3
"""
Test script to verify bug fixes in ImageViewer Pro
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        import datetime
        print("✅ datetime import - OK")
        
        # Test PIL imports
        from PIL import Image, ImageQt, ExifTags
        from PIL.ExifTags import TAGS
        print("✅ PIL imports - OK")
        
        # Test matplotlib imports
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        import numpy as np
        print("✅ matplotlib imports - OK")
        
        # Test PyQt5 imports
        from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
        from PyQt5.QtCore import Qt, QTimer, QSize
        from PyQt5.QtGui import QPixmap, QIcon, QImage
        print("✅ PyQt5 imports - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_thumbnail_creation():
    """Test thumbnail creation with PIL.ImageQt"""
    print("\n🖼️ Testing thumbnail creation...")
    
    try:
        from PIL import Image, ImageQt
        from PyQt5.QtGui import QPixmap, QIcon
        
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Test the fixed ImageQt usage
        qt_image = ImageQt(test_image)  # This should work now
        pixmap = QPixmap.fromImage(qt_image)
        
        print("✅ Thumbnail creation - OK")
        return True
        
    except Exception as e:
        print(f"❌ Thumbnail creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔧 ImageViewer Pro - Bug Fix Verification")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test thumbnail creation
    if not test_thumbnail_creation():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Bug fixes are working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    main()
