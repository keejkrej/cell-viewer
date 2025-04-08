"""View module for the cell viewer application."""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QSlider, QStatusBar)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class View(QMainWindow):
    # Define signals
    file_selected = Signal(str)  # Emitted when a file is selected
    page_changed = Signal(int)   # Emitted when page/slider changes
    autoplay_toggled = Signal(bool)  # Emitted when autoplay is toggled

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIFF Stack Viewer")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')  # Hide axes
        layout.addWidget(self.canvas)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Open file button
        self.open_button = QPushButton("Open TIFF")
        self.open_button.clicked.connect(self._handle_open_button)
        controls_layout.addWidget(self.open_button)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self._handle_slider_change)
        controls_layout.addWidget(self.slider)
        
        # Page counter
        self.page_label = QLabel("Page: 0/0")
        controls_layout.addWidget(self.page_label)
        
        # Autoplay button
        self.autoplay_button = QPushButton("Play")
        self.autoplay_button.setCheckable(True)
        self.autoplay_button.setEnabled(False)
        self.autoplay_button.clicked.connect(self._handle_autoplay_toggle)
        controls_layout.addWidget(self.autoplay_button)
        
        layout.addLayout(controls_layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Timer for autoplay
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # 100ms between frames (10 fps)
        
        # Store the current image display
        self.img_display = None

    @Slot()
    def _handle_open_button(self):
        """Internal slot to handle open button click"""
        file_path = self.get_file_path()
        if file_path:
            self.file_selected.emit(file_path)

    @Slot(int)
    def _handle_slider_change(self, value):
        """Internal slot to handle slider value changes"""
        self.page_changed.emit(value)

    @Slot(bool)
    def _handle_autoplay_toggle(self, checked):
        """Internal slot to handle autoplay button toggle"""
        self.autoplay_toggled.emit(checked)

    @Slot(object)
    def show_image(self, image):
        """Display the given image using matplotlib"""
        if image is None:
            return
            
        # Clear the previous image
        if self.img_display is not None:
            self.img_display.remove()
            
        # Display new image
        self.img_display = self.ax.imshow(image, cmap='gray')
        self.ax.set_position([0, 0, 1, 1])  # Make image fill the figure
        self.canvas.draw()

    @Slot(int, int)
    def update_page_info(self, current, total):
        """Update the page information display"""
        self.page_label.setText(f"Page: {current}/{total}")

    @Slot(str)
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

    @Slot(int, int)
    def set_slider_range(self, minimum, maximum):
        """Set the slider range and enable it"""
        self.slider.setRange(minimum, maximum)
        self.slider.setEnabled(True)
        self.autoplay_button.setEnabled(True)
        self.slider.setValue(minimum)

    @Slot(bool)
    def set_autoplay_state(self, is_playing):
        """Update the autoplay button text based on state"""
        self.autoplay_button.setText("Pause" if is_playing else "Play")
        self.autoplay_button.setChecked(is_playing)

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        self.canvas.draw()  # Redraw the canvas to update image scaling 

    @Slot(bool)
    def set_visible(self, visible):
        """Show or hide the window"""
        if visible:
            self.show()
        else:
            self.hide() 