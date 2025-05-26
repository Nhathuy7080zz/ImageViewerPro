#!/usr/bin/env python3
"""
ImageViewer Pro - Professional Image Viewer Application
Author: Phan Nhật Huy
License: MIT License
Description: A modern, feature-rich image viewer with advanced capabilities
"""

import sys
import os
import subprocess
import json
import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

# Auto-install dependencies
def install_dependencies():
    """Auto-install required dependencies if not available"""
    required_packages = {
        'PyQt5': 'PyQt5',
        'PIL': 'Pillow',
        'matplotlib': 'matplotlib'
    }
    
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install dependencies before importing
install_dependencies()

# Now import the modules
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QScrollArea, QPushButton, QFileDialog, QSplitter,
        QListWidget, QListWidgetItem, QTextEdit, QAction, QMenuBar,
        QStatusBar, QFrame, QSlider, QSpinBox, QComboBox, QGroupBox,
        QGridLayout, QMessageBox, QProgressBar, QCheckBox
    )
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QPoint
    from PyQt5.QtGui import (
        QPixmap, QIcon, QPainter, QPen, QBrush, QFont, QPalette,
        QKeySequence, QCursor, QTransform
    )
except ImportError as e:
    print(f"Error importing PyQt5: {e}")
    sys.exit(1)

try:
    from PIL import Image, ImageQt, ExifTags
    from PIL.ExifTags import TAGS
except ImportError as e:
    print(f"Error importing Pillow: {e}")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
except ImportError as e:
    print(f"Error importing matplotlib: {e}")
    sys.exit(1)


class HistogramWidget(QWidget):
    """Custom widget for displaying image histograms"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_image = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(6, 4), dpi=80)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.show_rgb = QCheckBox("RGB")
        self.show_rgb.setChecked(True)
        self.show_rgb.stateChanged.connect(self.update_histogram)
        
        self.show_luminance = QCheckBox("Luminance")
        self.show_luminance.setChecked(False)
        self.show_luminance.stateChanged.connect(self.update_histogram)
        
        controls_layout.addWidget(self.show_rgb)
        controls_layout.addWidget(self.show_luminance)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
    def set_image(self, image_path: str):
        """Set the current image and update histogram"""
        try:
            self.current_image = Image.open(image_path)
            if self.current_image.mode != 'RGB':
                self.current_image = self.current_image.convert('RGB')
            self.update_histogram()
        except Exception as e:
            print(f"Error loading image for histogram: {e}")
            
    def update_histogram(self):
        """Update the histogram display"""
        if not self.current_image:
            return
            
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Convert PIL image to numpy array
        img_array = np.array(self.current_image)
        
        if self.show_rgb.isChecked():
            # RGB histogram
            colors = ['red', 'green', 'blue']
            for i, color in enumerate(colors):
                ax.hist(img_array[:, :, i].ravel(), bins=256, 
                       color=color, alpha=0.6, label=color.title())
            ax.legend()
            
        if self.show_luminance.isChecked():
            # Luminance histogram
            luminance = 0.299 * img_array[:, :, 0] + 0.587 * img_array[:, :, 1] + 0.114 * img_array[:, :, 2]
            ax.hist(luminance.ravel(), bins=256, color='gray', alpha=0.8, label='Luminance')
            ax.legend()
            
        ax.set_xlim(0, 255)
        ax.set_xlabel('Pixel Value')
        ax.set_ylabel('Frequency')
        ax.set_title('Image Histogram')
        ax.grid(True, alpha=0.3)
        
        self.canvas.draw()


class ImageLabel(QLabel):
    """Custom QLabel for displaying images with zoom and pan capabilities"""
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("border: 1px solid gray;")
        
        # Image properties
        self.original_pixmap = None
        self.scale_factor = 1.0
        self.rotation_angle = 0
        self.pan_offset = QPoint(0, 0)
        self.dragging = False
        self.last_pan_point = QPoint()
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
    def set_image(self, pixmap: QPixmap):
        """Set the image to display"""
        self.original_pixmap = pixmap
        self.scale_factor = 1.0
        self.rotation_angle = 0
        self.pan_offset = QPoint(0, 0)
        self.update_display()
        
    def update_display(self):
        """Update the displayed image with current transformations"""
        if not self.original_pixmap:
            return
            
        # Apply rotation
        transform = QTransform()
        transform.rotate(self.rotation_angle)
        rotated_pixmap = self.original_pixmap.transformed(transform, Qt.SmoothTransformation)
        
        # Apply scaling
        scaled_size = rotated_pixmap.size() * self.scale_factor
        scaled_pixmap = rotated_pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.setPixmap(scaled_pixmap)
        
    def zoom_in(self):
        """Zoom in by 25%"""
        self.scale_factor *= 1.25
        self.update_display()
        
    def zoom_out(self):
        """Zoom out by 25%"""
        self.scale_factor *= 0.8
        self.update_display()
        
    def zoom_fit(self):
        """Fit image to widget size"""
        if not self.original_pixmap:
            return
            
        widget_size = self.size()
        pixmap_size = self.original_pixmap.size()
        
        scale_x = widget_size.width() / pixmap_size.width()
        scale_y = widget_size.height() / pixmap_size.height()
        
        self.scale_factor = min(scale_x, scale_y) * 0.9  # 90% to leave some margin
        self.pan_offset = QPoint(0, 0)
        self.update_display()
        
    def zoom_actual(self):
        """Show image at actual size (100%)"""
        self.scale_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()
        
    def rotate_left(self):
        """Rotate image 90 degrees counter-clockwise"""
        self.rotation_angle = (self.rotation_angle - 90) % 360
        self.update_display()
        
    def rotate_right(self):
        """Rotate image 90 degrees clockwise"""
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.update_display()
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
    def mousePressEvent(self, event):
        """Handle mouse press for panning"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pan_point = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for panning"""
        if self.dragging:
            delta = event.pos() - self.last_pan_point
            self.pan_offset += delta
            self.last_pan_point = event.pos()
            # Note: Pan functionality would need additional implementation
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))


class ThumbnailWidget(QListWidget):
    """Custom widget for displaying image thumbnails"""
    
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(120, 120))
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(5)
        self.setUniformItemSizes(True)
        
        # Store image paths
        self.image_paths = []
        
    def load_directory(self, directory: str):
        """Load all images from a directory"""
        self.clear()
        self.image_paths.clear()
        
        # Supported image formats
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico', '.svg'}
        
        try:
            directory_path = Path(directory)
            for file_path in directory_path.iterdir():
                if file_path.suffix.lower() in supported_formats:
                    self.add_thumbnail(str(file_path))
        except Exception as e:
            print(f"Error loading directory: {e}")
            
    def add_thumbnail(self, image_path: str):
        """Add a thumbnail for an image"""
        try:            # Create thumbnail
            image = Image.open(image_path)
            image.thumbnail((120, 120), Image.Resampling.LANCZOS)
            
            # Convert PIL image to bytes and then to QPixmap
            import io
            byte_array = io.BytesIO()
            image.save(byte_array, format='PNG')
            byte_array.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array.getvalue())
            
            # Create list item
            item = QListWidgetItem()
            item.setIcon(QIcon(pixmap))
            item.setText(Path(image_path).name)
            item.setToolTip(image_path)
            
            self.addItem(item)
            self.image_paths.append(image_path)
            
        except Exception as e:
            print(f"Error creating thumbnail for {image_path}: {e}")
            
    def get_selected_image_path(self) -> Optional[str]:
        """Get the path of the currently selected image"""
        current_row = self.currentRow()
        if 0 <= current_row < len(self.image_paths):
            return self.image_paths[current_row]
        return None


class MetadataWidget(QTextEdit):
    """Widget for displaying image metadata and EXIF information"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumWidth(300)
        self.setFont(QFont("Consolas", 9))
        
    def display_metadata(self, image_path: str):
        """Display metadata for the given image"""
        try:
            # Basic file information
            file_path = Path(image_path)
            file_stat = file_path.stat()
            
            metadata_text = f"""📁 <b>File Information</b>
📄 <b>Name:</b> {file_path.name}
📂 <b>Directory:</b> {file_path.parent}
📏 <b>Size:</b> {self.format_file_size(file_stat.st_size)}
📅 <b>Modified:</b> {self.format_timestamp(file_stat.st_mtime)}

"""
            
            # Image information
            try:
                with Image.open(image_path) as img:
                    metadata_text += f"""🖼️ <b>Image Properties</b>
📐 <b>Dimensions:</b> {img.size[0]} × {img.size[1]} pixels
🎨 <b>Mode:</b> {img.mode}
📋 <b>Format:</b> {img.format}

"""
                    
                    # EXIF data
                    exif_data = img._getexif()
                    if exif_data:
                        metadata_text += "📸 <b>EXIF Data</b>\n"
                        
                        # Key EXIF tags we want to display
                        important_tags = {
                            'Make': '📱 Camera Make',
                            'Model': '📷 Camera Model',
                            'DateTime': '📅 Date Taken',
                            'ExifImageWidth': '📐 EXIF Width',
                            'ExifImageHeight': '📐 EXIF Height',
                            'Orientation': '🔄 Orientation',
                            'XResolution': '🔍 X Resolution',
                            'YResolution': '🔍 Y Resolution',
                            'Flash': '⚡ Flash',
                            'FocalLength': '🔍 Focal Length',
                            'ISOSpeedRatings': '📊 ISO',
                            'ExposureTime': '⏱️ Exposure Time',
                            'FNumber': '🕳️ F-Number',
                            'WhiteBalance': '⚖️ White Balance',
                            'ColorSpace': '🌈 Color Space'
                        }
                        
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag in important_tags:
                                emoji_tag = important_tags[tag]
                                metadata_text += f"<b>{emoji_tag}:</b> {value}\n"
                    else:
                        metadata_text += "📸 <i>No EXIF data available</i>\n"
                        
            except Exception as e:
                metadata_text += f"❌ <b>Error reading image:</b> {str(e)}\n"
                
        except Exception as e:
            metadata_text = f"❌ <b>Error reading file:</b> {str(e)}"
            
        self.setHtml(metadata_text)
        
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
        
    def format_timestamp(self, timestamp: float) -> str:
        """Format timestamp in readable format"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class ImageViewer(QMainWindow):
    """Main ImageViewer Pro application"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.image_list = []
        self.current_index = 0
        self.is_fullscreen = False
        self.dark_theme = False
        
        self.setup_ui()
        self.setup_menus()
        self.setup_shortcuts()
        self.apply_theme()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("ImageViewer Pro v2.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for three panels
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Left panel - Thumbnails
        self.thumbnail_widget = ThumbnailWidget()
        self.thumbnail_widget.itemClicked.connect(self.on_thumbnail_clicked)
        self.splitter.addWidget(self.thumbnail_widget)
        
        # Center panel - Main image display
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        # Image display area
        self.scroll_area = QScrollArea()
        self.image_label = ImageLabel()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        center_layout.addWidget(self.scroll_area)
        
        # Image controls
        controls_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("🔍+ Zoom In")
        self.zoom_in_btn.clicked.connect(self.image_label.zoom_in)
        
        self.zoom_out_btn = QPushButton("🔍- Zoom Out")
        self.zoom_out_btn.clicked.connect(self.image_label.zoom_out)
        
        self.zoom_fit_btn = QPushButton("📏 Fit")
        self.zoom_fit_btn.clicked.connect(self.image_label.zoom_fit)
        
        self.zoom_actual_btn = QPushButton("1️⃣ Actual")
        self.zoom_actual_btn.clicked.connect(self.image_label.zoom_actual)
        
        self.rotate_left_btn = QPushButton("↺ Rotate Left")
        self.rotate_left_btn.clicked.connect(self.image_label.rotate_left)
        
        self.rotate_right_btn = QPushButton("↻ Rotate Right")
        self.rotate_right_btn.clicked.connect(self.image_label.rotate_right)
        
        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.zoom_fit_btn)
        controls_layout.addWidget(self.zoom_actual_btn)
        controls_layout.addWidget(self.rotate_left_btn)
        controls_layout.addWidget(self.rotate_right_btn)
        controls_layout.addStretch()
        
        center_layout.addLayout(controls_layout)
        self.splitter.addWidget(center_widget)
        
        # Right panel - Metadata and histogram
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Metadata display
        metadata_group = QGroupBox("📋 Image Information")
        metadata_layout = QVBoxLayout(metadata_group)
        self.metadata_widget = MetadataWidget()
        metadata_layout.addWidget(self.metadata_widget)
        right_layout.addWidget(metadata_group)
        
        # Histogram display
        histogram_group = QGroupBox("📊 Histogram")
        histogram_layout = QVBoxLayout(histogram_group)
        self.histogram_widget = HistogramWidget()
        histogram_layout.addWidget(self.histogram_widget)
        right_layout.addWidget(histogram_group)
        
        self.splitter.addWidget(right_widget)
        
        # Set splitter proportions
        self.splitter.setSizes([250, 800, 350])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Open an image to start")
        
    def setup_menus(self):
        """Setup application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('📁 File')
        
        open_action = QAction('📂 Open Image...', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction('📁 Open Folder...', self)
        open_folder_action.setShortcut('Ctrl+Shift+O')
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('🚪 Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('👁️ View')
        
        fullscreen_action = QAction('🖥️ Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        view_menu.addSeparator()
        
        theme_action = QAction('🌙 Toggle Dark Theme', self)
        theme_action.setShortcut('Ctrl+T')
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Navigation menu
        nav_menu = menubar.addMenu('🧭 Navigation')
        
        prev_action = QAction('⬅️ Previous Image', self)
        prev_action.setShortcut('Left')
        prev_action.triggered.connect(self.previous_image)
        nav_menu.addAction(prev_action)
        
        next_action = QAction('➡️ Next Image', self)
        next_action.setShortcut('Right')
        next_action.triggered.connect(self.next_image)
        nav_menu.addAction(next_action)
        
        # Help menu
        help_menu = menubar.addMenu('❓ Help')
        
        about_action = QAction('ℹ️ About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Additional shortcuts not covered by menu actions
        from PyQt5.QtWidgets import QShortcut
        
        # Zoom shortcuts
        QShortcut(QKeySequence("Ctrl+="), self, self.image_label.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.image_label.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.image_label.zoom_actual)
        QShortcut(QKeySequence("Ctrl+9"), self, self.image_label.zoom_fit)
        
        # Rotation shortcuts
        QShortcut(QKeySequence("Ctrl+L"), self, self.image_label.rotate_left)
        QShortcut(QKeySequence("Ctrl+R"), self, self.image_label.rotate_right)
        
    def apply_theme(self):
        """Apply current theme to the application"""
        if self.dark_theme:
            # Dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #404040;
                    color: #ffffff;
                    border-bottom: 1px solid #555555;
                }
                QMenuBar::item:selected {
                    background-color: #555555;
                }
                QMenu {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
                QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QPushButton:pressed {
                    background-color: #666666;
                }
                QListWidget {
                    background-color: #353535;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QTextEdit {
                    background-color: #353535;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 2px solid #555555;
                    border-radius: 5px;
                    margin: 5px 0px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0px 5px 0px 5px;
                }
                QStatusBar {
                    background-color: #404040;
                    color: #ffffff;
                    border-top: 1px solid #555555;
                }
                QSplitter::handle {
                    background-color: #555555;
                }
            """)
        else:
            # Light theme (default)
            self.setStyleSheet("")
            
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.dark_theme = not self.dark_theme
        self.apply_theme()
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
            
    def open_image(self):
        """Open a single image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.webp *.ico *.svg);;All Files (*)"
        )
        
        if file_path:
            self.load_image(file_path)
            
            # Load directory for navigation
            directory = os.path.dirname(file_path)
            self.thumbnail_widget.load_directory(directory)
            
            # Find current image in list
            filename = os.path.basename(file_path)
            for i, path in enumerate(self.thumbnail_widget.image_paths):
                if os.path.basename(path) == filename:
                    self.current_index = i
                    self.thumbnail_widget.setCurrentRow(i)
                    break
                    
    def open_folder(self):
        """Open a folder and load all images"""
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        
        if folder_path:
            self.thumbnail_widget.load_directory(folder_path)
            if self.thumbnail_widget.image_paths:
                self.current_index = 0
                self.thumbnail_widget.setCurrentRow(0)
                self.load_image(self.thumbnail_widget.image_paths[0])
                
    def load_image(self, image_path: str):
        """Load and display an image"""
        try:
            # Load and display image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.status_bar.showMessage(f"❌ Failed to load image: {image_path}")
                return
                
            self.image_label.set_image(pixmap)
            self.current_image_path = image_path
            
            # Update metadata
            self.metadata_widget.display_metadata(image_path)
            
            # Update histogram
            self.histogram_widget.set_image(image_path)
            
            # Update status bar
            filename = os.path.basename(image_path)
            self.status_bar.showMessage(f"📁 {filename} - {pixmap.width()}×{pixmap.height()}")
            
            # Update window title
            self.setWindowTitle(f"ImageViewer Pro v2.0 - {filename}")
            
        except Exception as e:
            self.status_bar.showMessage(f"❌ Error loading image: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load image:\n{str(e)}")
            
    def on_thumbnail_clicked(self, item):
        """Handle thumbnail click"""
        row = self.thumbnail_widget.row(item)
        if 0 <= row < len(self.thumbnail_widget.image_paths):
            self.current_index = row
            self.load_image(self.thumbnail_widget.image_paths[row])
            
    def previous_image(self):
        """Navigate to previous image"""
        if self.thumbnail_widget.image_paths and self.current_index > 0:
            self.current_index -= 1
            self.thumbnail_widget.setCurrentRow(self.current_index)
            self.load_image(self.thumbnail_widget.image_paths[self.current_index])
            
    def next_image(self):
        """Navigate to next image"""
        if (self.thumbnail_widget.image_paths and 
            self.current_index < len(self.thumbnail_widget.image_paths) - 1):
            self.current_index += 1
            self.thumbnail_widget.setCurrentRow(self.current_index)
            self.load_image(self.thumbnail_widget.image_paths[self.current_index])
            
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Left:
            self.previous_image()
        elif event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Space:
            self.next_image()
        else:
            super().keyPressEvent(event)
            
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>🖼️ ImageViewer Pro v2.0</h2>
        <p><b>Professional Image Viewer Application</b></p>
        
        <p><b>👨‍💻 Author:</b> Phan Nhật Huy</p>
        <p><b>📧 Email:</b> nhathuy7080zz@gmail.com</p>
        <p><b>📍 Location:</b> Ho Chi Minh, Vietnam</p>
        
        <h3>✨ Features:</h3>
        <ul>
            <li>🔍 Advanced zoom and pan controls</li>
            <li>📁 Thumbnail browser with directory navigation</li>
            <li>📊 Real-time color histogram analysis</li>
            <li>📋 Comprehensive EXIF metadata display</li>
            <li>🔄 Image rotation (90° increments)</li>
            <li>🌙 Dark/Light theme switching</li>
            <li>🖥️ Fullscreen viewing mode</li>
            <li>⌨️ Extensive keyboard shortcuts</li>
            <li>🎨 Support for multiple image formats</li>
        </ul>
        
        <h3>🎯 Supported Formats:</h3>
        <p>JPG, PNG, BMP, GIF, TIFF, WebP, ICO, SVG</p>
        
        <h3>⌨️ Keyboard Shortcuts:</h3>
        <ul>
            <li><b>Ctrl+O:</b> Open Image</li>
            <li><b>Ctrl+Shift+O:</b> Open Folder</li>
            <li><b>F11:</b> Toggle Fullscreen</li>
            <li><b>Ctrl+T:</b> Toggle Theme</li>
            <li><b>Left/Right:</b> Navigate Images</li>
            <li><b>Ctrl++/-:</b> Zoom In/Out</li>
            <li><b>Ctrl+0:</b> Actual Size</li>
            <li><b>Ctrl+9:</b> Fit to Window</li>
            <li><b>Ctrl+L/R:</b> Rotate Left/Right</li>
        </ul>
        
        <p><small>Built with PyQt5, Pillow, and Matplotlib</small></p>
        """
        
        QMessageBox.about(self, "About ImageViewer Pro", about_text)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("ImageViewer Pro")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Phan Nhật Huy")
    
    # Set application icon (if available)
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass
    
    # Create and show main window
    viewer = ImageViewer()
    viewer.show()
    
    # Auto-open image if provided as command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if os.path.isfile(image_path):
            viewer.load_image(image_path)
        elif os.path.isdir(image_path):
            viewer.thumbnail_widget.load_directory(image_path)
            if viewer.thumbnail_widget.image_paths:
                viewer.load_image(viewer.thumbnail_widget.image_paths[0])
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
