#!/usr/bin/env python3
"""
Quick verification test for ImageViewer Pro
Tests basic functionality without GUI interaction
"""

import sys
import os

def test_basic_functionality():
    """Test basic import and class instantiation"""
    try:
        print("🔍 Testing basic functionality...")
        
        # Test imports
        import main
        print("✅ Main module imported successfully")
        
        # Test that all required classes exist
        classes_to_check = [
            'ThumbnailWorker', 'ImageLabel', 'BeautifulThumbnailWidget',
            'BeautifulMetadataWidget', 'BeautifulHistogramWidget', 'ImageViewer'
        ]
        
        for class_name in classes_to_check:
            if hasattr(main, class_name):
                print(f"✅ Class {class_name} found")
            else:
                print(f"❌ Class {class_name} NOT found")
                return False
        
        print("🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_dependencies():
    """Test that all dependencies are available"""
    try:
        print("\n🔍 Testing dependencies...")
        
        dependencies = [
            'PyQt5', 'PIL', 'matplotlib', 'numpy'
        ]
        
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"✅ {dep} available")
            except ImportError:
                print(f"❌ {dep} NOT available")
                return False
        
        print("🎉 All dependencies available!")
        return True
        
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 ImageViewer Pro - Quick Verification Test")
    print("=" * 50)
    
    success = True
    success &= test_dependencies()
    success &= test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! ImageViewer Pro is ready to run.")
        print("💡 You can now start the application with: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    sys.exit(0 if success else 1)
