#!/usr/bin/env python3
"""
Quick test for ImageQt thumbnail creation
"""

import sys
import os
from pathlib import Path

def test_imageqt():
    """Test ImageQt thumbnail creation"""
    print("🧪 Testing ImageQt thumbnail creation...")
    
    try:        # Import required modules
        from PIL import Image, ImageQt
        from PyQt5.QtWidgets import QApplication
        
        # Create QApplication (required for Qt operations)
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
          # Test the fixed ImageQt usage
        print("  🔧 Testing ImageQt.toqpixmap() call...")
        pixmap = ImageQt.toqpixmap(test_image)
        print("  ✅ ImageQt.toqpixmap() - SUCCESS")
        
        print(f"  📏 Pixmap size: {pixmap.width()}x{pixmap.height()}")
        print("🎉 All thumbnail creation tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_imageqt()
