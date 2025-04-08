"""View module for the cell viewer application."""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QSlider, QStatusBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap

class View(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIFF Stack Viewer")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Open file button
        self.open_button = QPushButton("Open TIFF")
        controls_layout.addWidget(self.open_button)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        controls_layout.addWidget(self.slider)
        
        # Page counter
        self.page_label = QLabel("Page: 0/0")
        controls_layout.addWidget(self.page_label)
        
        layout.addLayout(controls_layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def show_image(self, image):
        """Display the given image in the label"""
        if image is None:
            return
            
        # Convert to QImage
        height, width = image.shape
        bytes_per_line = width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        
        # Scale image to fit label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def update_page_info(self, current, total):
        """Update the page information display"""
        self.page_label.setText(f"Page: {current}/{total}")

    def show_status_message(self, message):
        """Show a message in the status bar"""
        self.statusBar.showMessage(message)

    def get_file_path(self):
        """Open file dialog and return selected file path"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open TIFF File",
            "",
            "TIFF Files (*.tif *.tiff)"
        )
        return file_name

    def set_slider_range(self, minimum, maximum):
        """Set the slider range and enable it"""
        self.slider.setRange(minimum, maximum)
        self.slider.setEnabled(True)
        self.slider.setValue(minimum) 