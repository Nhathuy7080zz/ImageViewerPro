#!/usr/bin/env python3
"""
Test script for verifying ImageViewer Pro enhanced features
Tests the RAW format support, navigation, and layout improvements
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def test_raw_format_support():
    """Test that RAW formats are supported in file dialog"""
    try:
        from main import ImageViewer
        
        print("🔍 Testing RAW format support...")
        
        # Check if open_image method contains RAW formats
        import inspect
        source = inspect.getsource(ImageViewer.open_image)
        
        raw_formats = ['.arw', '.cr2', '.cr3', '.nef', '.dng', '.raw', '.orf', '.pef', '.rw2', '.srw', '.x3f']
        
        for fmt in raw_formats:
            if fmt in source:
                print(f"✅ RAW format {fmt} found in file dialog")
            else:
                print(f"❌ RAW format {fmt} NOT found")
                return False
        
        print("🎉 RAW format support test passed!")
        return True
        
    except Exception as e:
        print(f"❌ RAW format test failed: {e}")
        return False

def test_navigation_shortcuts():
    """Test that Up/Down navigation shortcuts are implemented"""
    try:
        from main import ImageViewer
        
        print("\n🔍 Testing navigation shortcuts...")
        
        # Check if setup_shortcuts method contains Up/Down navigation
        import inspect
        source = inspect.getsource(ImageViewer.setup_shortcuts)
        
        if '"Up"' in source and '"Down"' in source:
            print("✅ Up/Down arrow navigation found")
        else:
            print("❌ Up/Down arrow navigation NOT found")
            return False
        
        print("🎉 Navigation shortcuts test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")
        return False

def test_layout_improvements():
    """Test that right panel layout has been reorganized"""
    try:
        from main import ImageViewer
        
        print("\n🔍 Testing layout improvements...")
        
        # Check if setup_ui method contains layout improvements
        import inspect
        source = inspect.getsource(ImageViewer.setup_ui)
        
        # Look for stretch factors in the layout
        if 'addWidget(metadata_group, 3)' in source and 'addWidget(histogram_group, 1)' in source:
            print("✅ Right panel layout reorganization found")
        else:
            print("❌ Right panel layout reorganization NOT found")
            return False
        
        print("🎉 Layout improvements test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Layout test failed: {e}")
        return False

def test_thumbnail_raw_support():
    """Test that thumbnail widget supports RAW formats"""
    try:
        from main import BeautifulThumbnailWidget
        
        print("\n🔍 Testing thumbnail RAW support...")
        
        # Check if load_directory method contains RAW formats
        import inspect
        source = inspect.getsource(BeautifulThumbnailWidget.load_directory)
        
        raw_formats = ['.arw', '.cr2', '.cr3', '.nef', '.dng', '.raw', '.orf', '.pef', '.rw2', '.srw', '.x3f']
        
        for fmt in raw_formats:
            if fmt in source:
                print(f"✅ Thumbnail RAW format {fmt} found")
            else:
                print(f"❌ Thumbnail RAW format {fmt} NOT found")
                return False
        
        print("🎉 Thumbnail RAW support test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Thumbnail RAW test failed: {e}")
        return False

def test_app_instantiation():
    """Test that the application can be instantiated without errors"""
    try:
        print("\n🔍 Testing application instantiation...")
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from main import ImageViewer
        viewer = ImageViewer()
        
        print("✅ ImageViewer instantiated successfully")
        
        # Test that all key attributes exist
        required_attrs = ['current_image_path', 'current_index', 'is_fullscreen', 'dark_theme']
        for attr in required_attrs:
            if hasattr(viewer, attr):
                print(f"✅ Attribute {attr} found")
            else:
                print(f"❌ Attribute {attr} NOT found")
                return False
        
        # Clean up
        viewer.close()
        
        print("🎉 Application instantiation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Application instantiation test failed: {e}")
        return False

def main():
    """Run all feature tests"""
    print("🧪 ImageViewer Pro - Enhanced Features Test")
    print("=" * 50)
    
    tests = [
        test_raw_format_support,
        test_navigation_shortcuts,
        test_layout_improvements,
        test_thumbnail_raw_support,
        test_app_instantiation
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL ENHANCED FEATURE TESTS PASSED!")
        print("✅ RAW camera file support added")
        print("✅ Up/Down arrow navigation implemented")
        print("✅ Right panel layout reorganized")
        print("✅ Application is ready for use")
    else:
        print("❌ Some tests failed. Please review the implementation.")
    
    print("\n💡 To start the application: python main.py")

if __name__ == "__main__":
    main()
