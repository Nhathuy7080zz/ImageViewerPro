# ImageViewer Pro v2.0

🖼️ **Professional Image Viewer Application with Advanced Features**

**🎯 STATUS: FULLY FUNCTIONAL ✅** 
*All critical bugs fixed, zoom/pan optimized, dark mode enhanced, project cleaned up*

A modern, feature-rich image viewer built with PyQt5, offering professional-grade capabilities for image viewing, analysis, and management.

## 🌟 Features

### 🔍 Advanced Image Viewing
- **Multi-format Support**: JPG, PNG, BMP, GIF, TIFF, WebP, ICO, SVG
- **Advanced Zoom Controls**: Zoom in/out, fit to window, actual size (100%)
- **Smooth Pan & Navigate**: Mouse-based panning and keyboard navigation
- **Image Rotation**: 90-degree left/right rotation with smooth transitions
- **Fullscreen Mode**: Distraction-free viewing experience

### 📁 File Management
- **Thumbnail Browser**: Visual directory navigation with image previews
- **Directory Loading**: Open entire folders with automatic image discovery
- **Quick Navigation**: Arrow keys and space bar for rapid browsing
- **File Information**: Comprehensive file details and properties

### 📊 Professional Analysis Tools
- **Real-time Histogram**: RGB and luminance analysis with interactive controls
- **EXIF Metadata Display**: Complete camera and image information with emoji formatting
- **Image Properties**: Dimensions, file size, format, and modification dates
- **Color Analysis**: Detailed histogram visualization for image analysis

### 🎨 User Interface
- **Modern Design**: Clean, professional three-panel layout
- **Dark/Light Themes**: Toggle between comfortable viewing modes
- **Responsive Layout**: Resizable panels with intelligent sizing
- **Status Information**: Real-time feedback and image details
- **Emoji Integration**: User-friendly icons and visual indicators

### ⌨️ Keyboard Shortcuts
- **Ctrl+O**: Open Image
- **Ctrl+Shift+O**: Open Folder
- **F11**: Toggle Fullscreen
- **Ctrl+T**: Toggle Dark/Light Theme
- **Left/Right**: Navigate Previous/Next Image
- **Space**: Next Image
- **Ctrl++/-**: Zoom In/Out
- **Ctrl+0**: Actual Size (100%)
- **Ctrl+9**: Fit to Window
- **Ctrl+L/R**: Rotate Left/Right
- **Escape**: Exit Fullscreen

## 🚀 Quick Start

### Option 1: Run from Source
```bash
# Clone the repository
git clone https://github.com/Nhathuy7080zz/ImageViewerPro.git
cd ImageViewerPro

# Install dependencies (auto-installed on first run)
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 2: Command Line Usage
```bash
# Open specific image
python main.py "path/to/image.jpg"

# Open directory
python main.py "path/to/image/directory"
```

## 🛠️ Installation

### Requirements
- **Python 3.7+**
- **PyQt5 5.15.0+**
- **Pillow 9.0.0+**
- **matplotlib 3.5.0+**

### Auto-Installation
The application automatically installs missing dependencies on first run:
- PyQt5 (GUI framework)
- Pillow (Image processing)
- matplotlib (Histogram visualization)

### Manual Installation
```bash
pip install PyQt5>=5.15.0 Pillow>=9.0.0 matplotlib>=3.5.0
```

## 🏗️ Building Executable

### Create Standalone Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Run the build script
python build.py
```

The executable will be created in the `dist/` directory with all dependencies included.

### Build Options
- **One-file executable**: Single `.exe` file
- **Directory distribution**: Folder with executable and libraries
- **Custom icon**: Professional application icon
- **Optimized size**: Compressed and optimized build

## 📁 Project Structure

```
ImageViewerPro/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── build.py            # Build script for executable
├── README.md           # Documentation
├── dist/               # Built executables (created during build)
└── build/              # Build cache (created during build)
```

## 🎯 Technical Details

### Architecture
- **Main Window**: QMainWindow with three-panel splitter layout
- **Image Display**: Custom QLabel with zoom, pan, and rotation capabilities
- **Thumbnail Browser**: QListWidget with custom image loading
- **Metadata Panel**: QTextEdit with rich HTML formatting
- **Histogram Widget**: matplotlib integration for real-time analysis

### Image Processing
- **PIL/Pillow**: High-quality image loading and processing
- **Qt Image Handling**: Efficient display and manipulation
- **EXIF Processing**: Automatic metadata extraction and formatting
- **Thumbnail Generation**: Fast preview creation with aspect ratio preservation

### Performance Optimizations
- **Lazy Loading**: Images loaded only when needed
- **Memory Management**: Efficient pixmap handling
- **Async Operations**: Non-blocking file operations
- **Cache System**: Smart thumbnail and metadata caching

## 🔧 Configuration

### Default Settings
- **Theme**: Light mode (toggle with Ctrl+T)
- **Panel Sizes**: 250px (thumbnails), 800px (main), 350px (info)
- **Zoom Factor**: 25% increments
- **Thumbnail Size**: 120x120 pixels

### Customization
Edit the source code to customize:
- Default window size and position
- Thumbnail dimensions
- Zoom increments
- Color schemes and themes
- Keyboard shortcuts

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Install missing dependencies
pip install PyQt5 Pillow matplotlib
```

**Image Not Loading**
- Check file format compatibility
- Verify file permissions
- Ensure file is not corrupted

**Performance Issues**
- Close other applications for more memory
- Use smaller image files for testing
- Check available disk space

### Error Reporting
If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Test with different image files
4. Check file and directory permissions

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

### Development Setup
```bash
git clone https://github.com/Nhathuy7080zz/ImageViewerPro.git
cd ImageViewerPro
pip install -r requirements.txt
python main.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Phan Nhật Huy**
- 📧 Email: nhathuy7080zz@gmail.com
- 🐙 GitHub: [@Nhathuy7080zz](https://github.com/Nhathuy7080zz)
- 📍 Location: Ho Chi Minh, Vietnam
- 🎓 Computer Engineering Technology - HCMC University of Technology and Education

## 🙏 Acknowledgments

- **PyQt5 Team**: For the excellent GUI framework
- **Pillow Contributors**: For powerful image processing capabilities
- **matplotlib Team**: For advanced plotting and visualization tools
- **Python Community**: For continuous support and inspiration

---

## 🚀 Recent Updates

### Version 2.0
- ✅ Complete application rewrite with modern architecture
- ✅ Added professional three-panel layout
- ✅ Implemented real-time histogram analysis
- ✅ Enhanced EXIF metadata display with emoji formatting
- ✅ Added dark/light theme switching
- ✅ Improved zoom and pan controls
- ✅ Added image rotation capabilities
- ✅ Enhanced keyboard shortcuts
- ✅ Auto-dependency installation
- ✅ Professional build system

### Coming Soon
- 🔄 Image editing tools (crop, resize, filters)
- 📤 Export and save functionality
- 🏷️ Image tagging and organization
- 🔍 Advanced search and filtering
- 📊 Batch processing capabilities
- 🌐 Cloud storage integration

## 🔧 Recent Updates & Bug Fixes

### ✅ Version 2.0.1 - Critical Bug Fixes (Latest)
- **Fixed Thumbnail Creation**: Resolved `'module' object is not callable` error by replacing problematic PIL.ImageQt with robust PIL → bytes → QPixmap conversion
- **Fixed Build Script**: Corrected indentation errors and file references in PyInstaller build scripts
- **Added Missing Imports**: Added `datetime` and `io` modules for proper functionality
- **Improved Error Handling**: Enhanced thumbnail creation with better error reporting
- **Performance Optimization**: More reliable thumbnail loading for large image directories

### 🛠️ Technical Improvements
- **Replaced PIL.ImageQt**: Due to compatibility issues, switched to PIL → BytesIO → QPixmap workflow
- **Build System Fixed**: All build scripts now properly reference `main.py` instead of missing files
- **Import Cleanup**: Resolved all missing module imports and dependencies
- **Code Stability**: Eliminated module callable errors and improved error handling

---

**⭐ Star this project if you find it useful!**
