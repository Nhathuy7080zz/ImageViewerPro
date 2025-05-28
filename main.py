#!/usr/bin/env python3
"""
ImageViewer Pro - High Performance Image Viewer Application
Optimized for fast startup and image loading with beautiful UI
Author: Phan Nhật Huy
License: MIT License
"""

import sys
import os
import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import io

# Fast imports - no auto-install for better startup speed
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
    from PIL import Image, ImageQt, ExifTags
    from PIL.ExifTags import TAGS
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)


class ThumbnailWorker(QThread):
    """Background worker for loading thumbnails asynchronously"""
    thumbnail_ready = pyqtSignal(str, QPixmap, str)  # path, pixmap, filename
    
    def __init__(self, image_paths, thumbnail_size=(120, 120)):
        super().__init__()
        self.image_paths = image_paths
        self.thumbnail_size = thumbnail_size
        self.should_stop = False
        
    def run(self):
        """Generate thumbnails in background with optimized settings"""
        for image_path in self.image_paths:
            if self.should_stop:
                break
                
            try:
                # Quick file existence check
                if not os.path.exists(image_path):
                    continue
                    
                # Fast thumbnail generation
                with Image.open(image_path) as image:
                    # Convert to RGB if necessary for faster processing
                    if image.mode in ('RGBA', 'P', 'LA'):
                        image = image.convert('RGB')
                    
                    # Use FAST resampling for speed
                    image.thumbnail(self.thumbnail_size, Image.Resampling.FAST)
                    
                    # Quick conversion to bytes using JPEG for speed
                    byte_array = io.BytesIO()
                    image.save(byte_array, format='JPEG', quality=75, optimize=True)
                    byte_array.seek(0)
                    
                    # Create QPixmap
                    pixmap = QPixmap()
                    pixmap.loadFromData(byte_array.getvalue())
                    
                    # Emit signal with result
                    filename = Path(image_path).name
                    self.thumbnail_ready.emit(image_path, pixmap, filename)
                    
            except Exception:
                # Skip problematic images silently for better performance
                continue
                
    def stop(self):
        """Stop the worker"""
        self.should_stop = True


class ImageLabel(QLabel):
    """Optimized image display widget with zoom and pan"""
    
    def __init__(self):
        super().__init__()
        self.original_pixmap = None
        self.scale_factor = 1.0
        self.rotation_angle = 0
        self.dragging = False
        self.last_pan_point = QPoint()
        self.scroll_area = None
        
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(100, 100)
        self.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
            }
        """)
        
    def set_scroll_area(self, scroll_area):
        """Set the parent scroll area for panning"""
        self.scroll_area = scroll_area
        
    def set_image(self, pixmap):
        """Set image with fast display"""
        self.original_pixmap = pixmap
        self.scale_factor = 1.0
        self.rotation_angle = 0
        self.update_display()
        
    def update_display(self):
        """Update image display with current transformations"""
        if not self.original_pixmap:
            return
            
        # Apply rotation if needed
        if self.rotation_angle != 0:
            transform = QTransform()
            transform.rotate(self.rotation_angle)
            rotated_pixmap = self.original_pixmap.transformed(transform, Qt.SmoothTransformation)
        else:
            rotated_pixmap = self.original_pixmap
        
        # Apply scaling
        if self.scale_factor != 1.0:
            scaled_size = rotated_pixmap.size() * self.scale_factor
            scaled_pixmap = rotated_pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            scaled_pixmap = rotated_pixmap
        
        # Update widget size for proper scrolling
        self.resize(scaled_pixmap.size())
        self.setPixmap(scaled_pixmap)
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming at cursor position"""
        if not self.original_pixmap:
            return
            
        # Store old scale and cursor position
        old_scale = self.scale_factor
        cursor_pos = event.pos()
        
        # Calculate zoom
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.25 if zoom_in else 0.8
        
        new_scale = self.scale_factor * zoom_factor
        new_scale = max(0.1, min(new_scale, 10.0))  # Limit zoom range
        
        if new_scale != self.scale_factor:
            self.scale_factor = new_scale
            self.update_display()
            
            # Adjust scroll position to zoom at cursor
            if self.scroll_area and old_scale != self.scale_factor:
                scale_ratio = self.scale_factor / old_scale
                h_bar = self.scroll_area.horizontalScrollBar()
                v_bar = self.scroll_area.verticalScrollBar()
                
                # Calculate new scroll positions
                new_h = int((h_bar.value() + cursor_pos.x()) * scale_ratio - cursor_pos.x())
                new_v = int((v_bar.value() + cursor_pos.y()) * scale_ratio - cursor_pos.y())
                
                h_bar.setValue(new_h)
                v_bar.setValue(new_v)
                
    def mousePressEvent(self, event):
        """Handle mouse press for panning"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pan_point = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for panning"""
        if self.dragging and self.scroll_area:
            delta = event.pos() - self.last_pan_point
            
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            
            self.last_pan_point = event.pos()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            
    def zoom_in(self):
        """Zoom in by 25%"""
        self.scale_factor *= 1.25
        self.scale_factor = min(self.scale_factor, 10.0)
        self.update_display()
        
    def zoom_out(self):
        """Zoom out by 25%"""
        self.scale_factor *= 0.8
        self.scale_factor = max(self.scale_factor, 0.1)
        self.update_display()
        
    def zoom_fit(self):
        """Fit image to window"""
        if not self.original_pixmap or not self.scroll_area:
            return
            
        viewport_size = self.scroll_area.viewport().size()
        pixmap_size = self.original_pixmap.size()
        
        scale_x = viewport_size.width() / pixmap_size.width()
        scale_y = viewport_size.height() / pixmap_size.height()
        
        self.scale_factor = min(scale_x, scale_y, 1.0)
        self.update_display()
        
    def zoom_actual(self):
        """Show actual size (100%)"""
        self.scale_factor = 1.0
        self.update_display()
        
    def rotate_left(self):
        """Rotate 90 degrees left"""
        self.rotation_angle = (self.rotation_angle - 90) % 360
        self.update_display()
        
    def rotate_right(self):
        """Rotate 90 degrees right"""
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.update_display()


class BeautifulThumbnailWidget(QListWidget):
    """High-performance thumbnail widget with beautiful styling"""
    
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(120, 120))
        self.setResizeMode(QListWidget.Adjust)
        self.setSpacing(8)
        self.setUniformItemSizes(True)
        self.setMovement(QListWidget.Static)
        
        # Beautiful styling
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                background-color: #2b2b2b;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
                border: 2px solid #14a085;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
                border: 2px solid #5a5a5a;
            }
        """)
        
        # Store paths and cache
        self.image_paths = []
        self.thumbnail_cache = {}
        self.thumbnail_worker = None
        
        # Create beautiful placeholder
        self.placeholder_pixmap = self.create_placeholder()
        
    def create_placeholder(self):
        """Create beautiful loading placeholder"""
        pixmap = QPixmap(120, 120)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gradient background
        gradient = QBrush(Qt.lightGray)
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 120, 120, 8, 8)
        
        # Camera icon
        painter.setPen(QPen(Qt.darkGray, 2))
        font = QFont()
        font.setPixelSize(32)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "📷")
        
        # Loading text
        font.setPixelSize(10)
        painter.setFont(font)
        painter.setPen(Qt.gray)
        painter.drawText(QPoint(30, 110), "Loading...")
        
        painter.end()
        return pixmap
        
    def load_directory(self, directory: str):
        """Load directory with async thumbnails"""        # Stop existing worker
        if self.thumbnail_worker and self.thumbnail_worker.isRunning():
            self.thumbnail_worker.stop()
            self.thumbnail_worker.wait()
            
        self.clear()
        self.image_paths.clear()
        self.thumbnail_cache.clear()
        
        # Fast file scanning - Enhanced with RAW format support
        supported_formats = {
            # Standard formats
            '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico',
            # RAW camera formats
            '.arw', '.cr2', '.cr3', '.nef', '.dng', '.raw', '.orf', '.pef', '.rw2', '.srw', '.x3f'
        }
        
        try:
            directory_path = Path(directory)
            image_files = []
            
            # Quick scan for image files
            for file_path in directory_path.iterdir():
                if (file_path.suffix.lower() in supported_formats and 
                    file_path.is_file() and file_path.stat().st_size > 0):
                    image_files.append(str(file_path))
                    
            if not image_files:
                return
                
            # Sort for consistent order
            image_files.sort()
            self.image_paths = image_files
            
            # Create placeholder items immediately
            for image_path in image_files:
                item = QListWidgetItem()
                item.setIcon(QIcon(self.placeholder_pixmap))
                item.setText(Path(image_path).name)
                item.setToolTip(f"📁 {Path(image_path).name}\n📏 {self.get_file_size(image_path)}")
                self.addItem(item)
            
            # Start async thumbnail loading
            self.thumbnail_worker = ThumbnailWorker(image_files)
            self.thumbnail_worker.thumbnail_ready.connect(self.on_thumbnail_ready)
            self.thumbnail_worker.start()
            
        except Exception as e:
            print(f"Error loading directory: {e}")
            
    def get_file_size(self, file_path):
        """Get formatted file size"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.1f} {unit}"
                size /= 1024
            return f"{size:.1f} TB"
        except:
            return "Unknown"
            
    def on_thumbnail_ready(self, image_path: str, pixmap: QPixmap, filename: str):
        """Update item with loaded thumbnail"""
        try:
            # Find and update item
            for i in range(self.count()):
                item = self.item(i)
                if item.toolTip().endswith(Path(image_path).name):
                    item.setIcon(QIcon(pixmap))
                    self.thumbnail_cache[image_path] = pixmap
                    break
        except Exception:
            pass  # Ignore errors for performance
            
    def cleanup(self):
        """Clean up worker thread"""
        if self.thumbnail_worker and self.thumbnail_worker.isRunning():
            self.thumbnail_worker.stop()
            self.thumbnail_worker.wait()


class BeautifulMetadataWidget(QTextEdit):
    """Beautiful metadata display widget"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(300)
        
        # Beautiful styling
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                padding: 8px;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                line-height: 1.4;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #0d7377;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #14a085;
            }
        """)
        
    def display_metadata(self, image_path: str):
        """Display comprehensive metadata with beautiful formatting"""
        try:
            file_path = Path(image_path)
            file_stat = file_path.stat()
            
            # Enhanced metadata with icons and formatting
            metadata_html = f"""
            <div style="color: #e0e0e0; line-height: 1.6;">
                <h3 style="color: #14a085; margin-bottom: 12px;">
                    📁 {file_path.name}
                </h3>
                
                <table style="width: 100%; border-spacing: 0;">
                    <tr><td style="color: #888; padding: 2px 8px 2px 0;">📏 Size:</td>
                        <td style="color: #e0e0e0; padding: 2px 0;">{self.format_size(file_stat.st_size)}</td></tr>
                    <tr><td style="color: #888; padding: 2px 8px 2px 0;">📅 Modified:</td>
                        <td style="color: #e0e0e0; padding: 2px 0;">{datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                    <tr><td style="color: #888; padding: 2px 8px 2px 0;">📂 Path:</td>
                        <td style="color: #888; font-size: 10px; padding: 2px 0;">{str(file_path.parent)}</td></tr>
                </table>
            """
            
            # Enhanced image info with EXIF
            try:
                with Image.open(image_path) as img:
                    metadata_html += f"""
                    <h4 style="color: #14a085; margin: 16px 0 8px 0;">🖼️ Image Properties</h4>
                    <table style="width: 100%; border-spacing: 0;">
                        <tr><td style="color: #888; padding: 2px 8px 2px 0;">Dimensions:</td>
                            <td style="color: #e0e0e0; padding: 2px 0;">{img.width} × {img.height} pixels</td></tr>
                        <tr><td style="color: #888; padding: 2px 8px 2px 0;">Color Mode:</td>
                            <td style="color: #e0e0e0; padding: 2px 0;">{img.mode}</td></tr>
                        <tr><td style="color: #888; padding: 2px 8px 2px 0;">Format:</td>
                            <td style="color: #e0e0e0; padding: 2px 0;">{img.format or 'Unknown'}</td></tr>
                    """
                    
                    # Add resolution
                    try:
                        megapixels = (img.width * img.height) / 1000000
                        metadata_html += f"""
                        <tr><td style="color: #888; padding: 2px 8px 2px 0;">Resolution:</td>
                            <td style="color: #e0e0e0; padding: 2px 0;">{megapixels:.1f} MP</td></tr>
                        """
                    except:
                        pass
                    
                    metadata_html += "</table>"
                    
                    # EXIF data
                    exif_data = img._getexif() if hasattr(img, '_getexif') else None
                    if exif_data:
                        metadata_html += """
                        <h4 style="color: #14a085; margin: 16px 0 8px 0;">📷 Camera Info</h4>
                        <table style="width: 100%; border-spacing: 0;">
                        """
                        
                        # Important EXIF tags
                        important_tags = {
                            'Make': '📱 Camera Make',
                            'Model': '📷 Camera Model',
                            'DateTime': '🕒 Date Taken',
                            'ExposureTime': '⏱️ Exposure',
                            'FNumber': '🔍 Aperture',
                            'ISOSpeedRatings': '🎞️ ISO',
                            'FocalLength': '🎯 Focal Length'
                        }
                        
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)
                            if tag in important_tags:
                                icon_name = important_tags[tag]
                                if isinstance(value, tuple) and len(value) == 2:
                                    value = f"{value[0]}/{value[1]}"
                                metadata_html += f"""
                                <tr><td style="color: #888; padding: 2px 8px 2px 0;">{icon_name}:</td>
                                    <td style="color: #e0e0e0; padding: 2px 0;">{str(value)[:50]}</td></tr>
                                """
                        
                        metadata_html += "</table>"
                        
            except Exception:
                metadata_html += """
                <p style="color: #ff6b6b; margin-top: 12px;">
                    ⚠️ Could not read image properties
                </p>
                """
                
            metadata_html += "</div>"
            self.setHtml(metadata_html)
            
        except Exception as e:
            self.setHtml(f"""
            <div style="color: #ff6b6b;">
                <h3>❌ Error Loading Metadata</h3>
                <p>{str(e)}</p>
            </div>
            """)
            
    def format_size(self, size_bytes):
        """Format file size with appropriate units"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


class BeautifulHistogramWidget(QWidget):
    """Beautiful histogram widget with enhanced styling"""
    
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(200)
        self.current_image = None
        
        # Enhanced matplotlib setup
        plt.style.use('dark_background')
        self.figure = Figure(figsize=(5, 2.5), dpi=100, facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        
    def set_image(self, image_path: str):
        """Set image for histogram with beautiful visualization"""
        try:
            # Load and process image
            with Image.open(image_path) as img:
                # Convert to RGB for consistent processing
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Sample image if too large for speed
                if img.width * img.height > 1000000:  # 1MP
                    img.thumbnail((800, 600), Image.Resampling.FAST)
                
                # Create beautiful histogram
                self.figure.clear()
                self.figure.patch.set_facecolor('#1e1e1e')
                
                ax = self.figure.add_subplot(111, facecolor='#1e1e1e')
                
                # Convert to numpy array
                data = np.array(img)
                
                # Create RGB histogram with beautiful styling
                colors = ['#ff4444', '#44ff44', '#4444ff']
                labels = ['Red', 'Green', 'Blue']
                
                for i, (color, label) in enumerate(zip(colors, labels)):
                    ax.hist(data[:,:,i].flatten(), bins=64, color=color, alpha=0.7, 
                           density=True, label=label, linewidth=0)
                
                # Beautiful styling
                ax.set_xlim(0, 255)
                ax.set_title('🎨 RGB Color Histogram', fontsize=12, color='#14a085', pad=10)
                ax.set_xlabel('Pixel Intensity', fontsize=10, color='#e0e0e0')
                ax.set_ylabel('Frequency', fontsize=10, color='#e0e0e0')
                
                # Style the axes
                ax.tick_params(colors='#888888', labelsize=8)
                ax.spines['bottom'].set_color('#3c3c3c')
                ax.spines['top'].set_color('#3c3c3c')
                ax.spines['right'].set_color('#3c3c3c')
                ax.spines['left'].set_color('#3c3c3c')
                
                # Add legend
                ax.legend(loc='upper right', fontsize=8, framealpha=0.8, 
                         facecolor='#2b2b2b', edgecolor='#3c3c3c')
                
                # Tight layout
                self.figure.tight_layout(pad=0.5)
                self.canvas.draw()
                
        except Exception:
            # Clear on error with message
            self.figure.clear()
            ax = self.figure.add_subplot(111, facecolor='#1e1e1e')
            ax.text(0.5, 0.5, '⚠️ Cannot generate histogram', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='#ff6b6b')
            ax.set_xticks([])
            ax.set_yticks([])
            self.canvas.draw()


class ImageViewer(QMainWindow):
    """High-performance ImageViewer Pro with beautiful interface"""
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.current_index = 0
        self.is_fullscreen = False
        self.dark_theme = True
        
        self.setup_ui()
        self.setup_menus()
        self.setup_shortcuts()
        self.apply_beautiful_theme()
        
    def closeEvent(self, event):
        """Handle app close with proper cleanup"""
        if hasattr(self, 'thumbnail_widget'):
            self.thumbnail_widget.cleanup()
        event.accept()
        
    def setup_ui(self):
        """Setup beautiful optimized UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main splitter layout
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(True)
        
        # Left panel - thumbnails
        left_widget = QWidget()
        left_widget.setMaximumWidth(300)
        left_widget.setMinimumWidth(250)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(8, 8, 4, 8)
        
        # Thumbnail browser with beautiful header
        thumbnail_group = QGroupBox("📁 Image Gallery")
        thumbnail_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #14a085;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: #1e1e1e;
            }
        """)
        
        thumbnail_layout = QVBoxLayout(thumbnail_group)
        thumbnail_layout.setContentsMargins(8, 8, 8, 8)
        
        self.thumbnail_widget = BeautifulThumbnailWidget()
        self.thumbnail_widget.itemClicked.connect(self.on_thumbnail_clicked)
        thumbnail_layout.addWidget(self.thumbnail_widget)
        
        left_layout.addWidget(thumbnail_group)
        self.splitter.addWidget(left_widget)
        
        # Center panel - image with beautiful frame
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(8)
        center_layout.setContentsMargins(4, 8, 4, 8)
        
        # Image display with beautiful frame
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
            }
        """)
        
        image_layout = QVBoxLayout(image_frame)
        image_layout.setContentsMargins(4, 4, 4, 4)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background-color: #2b2b2b;
                border-radius: 6px;
                width: 12px;
                height: 12px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background-color: #0d7377;
                border-radius: 6px;
                min-height: 20px;
                min-width: 20px;
            }
            QScrollBar::handle:hover {
                background-color: #14a085;
            }
        """)
        
        self.image_label = ImageLabel()
        self.image_label.set_scroll_area(self.scroll_area)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        image_layout.addWidget(self.scroll_area)
        
        center_layout.addWidget(image_frame)
        
        # Beautiful control panel
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setSpacing(8)
        controls_layout.setContentsMargins(8, 4, 8, 4)
        
        # Styled buttons
        button_style = """
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: 2px solid #14a085;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #14a085;
                border: 2px solid #1bb299;
            }            QPushButton:pressed {
                background-color: #0a5a5d;
            }
        """
        
        self.zoom_in_btn = QPushButton("🔍+ Zoom In")
        self.zoom_in_btn.setStyleSheet(button_style)
        self.zoom_in_btn.clicked.connect(self.image_label.zoom_in)
        
        self.zoom_out_btn = QPushButton("🔍- Zoom Out")
        self.zoom_out_btn.setStyleSheet(button_style)
        self.zoom_out_btn.clicked.connect(self.image_label.zoom_out)
        
        self.zoom_fit_btn = QPushButton("📐 Fit Window")
        self.zoom_fit_btn.setStyleSheet(button_style)
        self.zoom_fit_btn.clicked.connect(self.image_label.zoom_fit)
        
        self.zoom_actual_btn = QPushButton("1:1 Actual Size")
        self.zoom_actual_btn.setStyleSheet(button_style)
        self.zoom_actual_btn.clicked.connect(self.image_label.zoom_actual)
        
        self.rotate_left_btn = QPushButton("↺ Left")
        self.rotate_left_btn.setStyleSheet(button_style)
        self.rotate_left_btn.clicked.connect(self.image_label.rotate_left)
        
        self.rotate_right_btn = QPushButton("↻ Right")
        self.rotate_right_btn.setStyleSheet(button_style)
        self.rotate_right_btn.clicked.connect(self.image_label.rotate_right)
        
        controls_layout.addWidget(self.zoom_in_btn)
        controls_layout.addWidget(self.zoom_out_btn)
        controls_layout.addWidget(self.zoom_fit_btn)
        controls_layout.addWidget(self.zoom_actual_btn)
        
        # Add separator frame
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #3c3c3c;")
        controls_layout.addWidget(separator)
        
        controls_layout.addWidget(self.rotate_left_btn)
        controls_layout.addWidget(self.rotate_right_btn)
        controls_layout.addStretch()
        
        center_layout.addWidget(controls_frame)
        self.splitter.addWidget(center_widget)
        
        # Right panel - info with beautiful styling
        right_widget = QWidget()
        right_widget.setMaximumWidth(320)
        right_widget.setMinimumWidth(280)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(4, 8, 8, 8)
        
        # Metadata panel
        metadata_group = QGroupBox("📋 Image Information")
        metadata_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #14a085;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
            }            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: #1e1e1e;
            }
        """)
        
        metadata_layout = QVBoxLayout(metadata_group)
        metadata_layout.setContentsMargins(8, 8, 8, 8)
        
        self.metadata_widget = BeautifulMetadataWidget()
        metadata_layout.addWidget(self.metadata_widget)
        
        # Add metadata with expanded space (stretch factor of 3)
        right_layout.addWidget(metadata_group, 3)
        
        # Histogram panel positioned at bottom
        histogram_group = QGroupBox("📊 Color Analysis")
        histogram_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #14a085;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: #1e1e1e;
            }
        """)
        
        histogram_layout = QVBoxLayout(histogram_group)
        histogram_layout.setContentsMargins(8, 8, 8, 8)
        
        self.histogram_widget = BeautifulHistogramWidget()
        histogram_layout.addWidget(self.histogram_widget)
        
        # Add histogram at bottom with fixed space (stretch factor of 1)
        right_layout.addWidget(histogram_group, 1)
        
        self.splitter.addWidget(right_widget)
        
        # Configure splitter proportions
        self.splitter.setCollapsible(0, True)
        self.splitter.setCollapsible(1, False)
        self.splitter.setCollapsible(2, True)
        self.splitter.setSizes([300, 800, 320])
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.splitter)
        main_layout.setContentsMargins(4, 4, 4, 4)
        
        # Beautiful status bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border-top: 2px solid #3c3c3c;
                padding: 4px;
                font-size: 11px;
            }
        """)
        self.status_bar.showMessage("🚀 ImageViewer Pro v2.0 Ready - Open an image or folder to start")
        
        # Window settings
        self.setWindowTitle("🖼️ ImageViewer Pro v2.0 - High Performance Edition")
        self.setMinimumSize(1200, 700)
        self.resize(1600, 900)
        
    def setup_menus(self):
        """Setup beautiful menus"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border-bottom: 2px solid #3c3c3c;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #0d7377;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: 2px solid #3c3c3c;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0d7377;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("📁 File")
        
        open_action = QAction("🖼️ Open Image", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("📂 Open Folder", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
          # View menu
        view_menu = menubar.addMenu("👁️ View")
        
        fullscreen_action = QAction("🖥️ Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        theme_action = QAction("🎨 Toggle Theme", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        view_menu.addSeparator()
        
        # Zoom actions
        zoom_in_action = QAction("🔍+ Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.image_label.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("🔍- Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.image_label.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("📐 Fit to Window", self)
        zoom_fit_action.setShortcut("Ctrl+0")
        zoom_fit_action.triggered.connect(self.image_label.zoom_fit)
        view_menu.addAction(zoom_fit_action)
        
        zoom_actual_action = QAction("1️⃣ Actual Size", self)
        zoom_actual_action.setShortcut("Ctrl+1")
        zoom_actual_action.triggered.connect(self.image_label.zoom_actual)
        view_menu.addAction(zoom_actual_action)
        
        # Transform menu
        transform_menu = menubar.addMenu("🔄 Transform")
        
        rotate_left_action = QAction("↺ Rotate Left", self)
        rotate_left_action.setShortcut("Ctrl+L")
        rotate_left_action.triggered.connect(self.image_label.rotate_left)
        transform_menu.addAction(rotate_left_action)
        
        rotate_right_action = QAction("↻ Rotate Right", self)
        rotate_right_action.setShortcut("Ctrl+R")
        rotate_right_action.triggered.connect(self.image_label.rotate_right)
        transform_menu.addAction(rotate_right_action)
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Navigation shortcuts
        self.addAction(self.create_action("Left", self.previous_image))
        self.addAction(self.create_action("Right", self.next_image))
        self.addAction(self.create_action("Up", self.previous_image))    # Added up arrow navigation
        self.addAction(self.create_action("Down", self.next_image))      # Added down arrow navigation
        self.addAction(self.create_action("Space", self.next_image))
        self.addAction(self.create_action("Backspace", self.previous_image))
        
    def create_action(self, shortcut, slot):
        """Helper to create action with shortcut"""
        action = QAction(self)
        action.setShortcut(shortcut)
        action.triggered.connect(slot)
        return action
        
    def apply_beautiful_theme(self):
        """Apply beautiful dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QSplitter::handle {
                background-color: #3c3c3c;
                width: 3px;
                height: 3px;
            }
            QSplitter::handle:hover {
                background-color: #0d7377;
            }
        """)
        
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_theme = not self.dark_theme
        if self.dark_theme:
            self.apply_beautiful_theme()
        else:
            # Light theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }            """)
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen
        
    def open_image(self):
        """Open single image with beautiful dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "🖼️ Open Image File", "", 
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp *.ico *.arw *.cr2 *.cr3 *.nef *.dng *.raw *.orf *.pef *.rw2 *.srw *.x3f);;Standard Images (*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp *.ico);;RAW Images (*.arw *.cr2 *.cr3 *.nef *.dng *.raw *.orf *.pef *.rw2 *.srw *.x3f);;All Files (*)"
        )
        
        if file_path:
            self.load_image(file_path)
            # Load other images in same directory
            directory = str(Path(file_path).parent)
            self.thumbnail_widget.load_directory(directory)
            
    def open_folder(self):
        """Open folder with beautiful dialog"""
        folder_path = QFileDialog.getExistingDirectory(self, "📂 Open Image Folder")
        
        if folder_path:
            self.thumbnail_widget.load_directory(folder_path)
            if self.thumbnail_widget.image_paths:
                self.current_index = 0
                self.thumbnail_widget.setCurrentRow(0)
                self.load_image(self.thumbnail_widget.image_paths[0])
                
    def load_image(self, image_path: str):
        """Load image with optimized performance and beautiful display"""
        try:
            # Fast pixmap loading
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.status_bar.showMessage(f"❌ Failed to load: {os.path.basename(image_path)}")
                return
                
            # Immediate display
            self.image_label.set_image(pixmap)
            self.current_image_path = image_path
            self.image_label.zoom_fit()
            
            # Beautiful status update
            filename = os.path.basename(image_path)
            self.status_bar.showMessage(
                f"🖼️ {filename} • 📏 {pixmap.width()}×{pixmap.height()} • 🔍 {int(self.image_label.scale_factor*100)}%"
            )
            self.setWindowTitle(f"🖼️ ImageViewer Pro v2.0 - {filename}")
            
            # Async metadata and histogram loading for performance
            QTimer.singleShot(50, lambda: self.load_metadata_async(image_path))
            QTimer.singleShot(100, lambda: self.load_histogram_async(image_path))
            
        except Exception as e:
            self.status_bar.showMessage(f"❌ Error loading image: {str(e)}")
            
    def load_metadata_async(self, image_path: str):
        """Load metadata asynchronously"""
        if self.current_image_path == image_path:
            try:
                self.metadata_widget.display_metadata(image_path)
            except Exception:
                pass
                
    def load_histogram_async(self, image_path: str):
        """Load histogram asynchronously"""
        if self.current_image_path == image_path:
            try:
                self.histogram_widget.set_image(image_path)
            except Exception:
                pass
                
    def on_thumbnail_clicked(self, item):
        """Handle thumbnail click with smooth transition"""
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


def main():
    """Main application function with error handling"""
    app = QApplication(sys.argv)
    app.setApplicationName("ImageViewer Pro")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Phan Nhật Huy")
    
    try:
        # Create and show main window
        viewer = ImageViewer()
        viewer.show()
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            path = sys.argv[1]
            if os.path.isfile(path):
                viewer.load_image(path)
                directory = str(Path(path).parent)
                viewer.thumbnail_widget.load_directory(directory)
            elif os.path.isdir(path):
                viewer.thumbnail_widget.load_directory(path)
                if viewer.thumbnail_widget.image_paths:
                    viewer.load_image(viewer.thumbnail_widget.image_paths[0])
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
