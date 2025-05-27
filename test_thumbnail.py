#!/usr/bin/env python3
"""
Quick test for thumbnail creation without ImageQt
"""

import sys
import os
import io
from pathlib import Path

def test_thumbnail_creation():
    """Test thumbnail creation using PIL -> bytes -> QPixmap"""
    print("🧪 Testing thumbnail creation (PIL -> bytes -> QPixmap)...")
    
    try:
        # Import required modules
        from PIL import Image
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QPixmap
        
        # Create QApplication (required for Qt operations)
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Test the new approach: PIL -> bytes -> QPixmap
        print("  🔧 Testing PIL -> bytes -> QPixmap conversion...")
        byte_array = io.BytesIO()
        test_image.save(byte_array, format='PNG')
        byte_array.seek(0)
        
        pixmap = QPixmap()
        success = pixmap.loadFromData(byte_array.getvalue())
        
        if success:
            print("  ✅ PIL -> bytes -> QPixmap - SUCCESS")
            print(f"  📏 Pixmap size: {pixmap.width()}x{pixmap.height()}")
            print("🎉 All thumbnail creation tests PASSED!")
            return True
        else:
            print("  ❌ Failed to load pixmap from bytes")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_thumbnail_creation()
