"""View module for the cell viewer application."""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QSlider, QStatusBar)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
import os
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainView(QMainWindow):
    # Define signals
    file_selected = Signal(str)  # Emitted when a file is selected
    frame_changed = Signal(int)   # Emitted when frame/slider changes
    autoplay_toggled = Signal(bool)  # Emitted when autoplay is toggled
    interval_marked = Signal(int, int)  # Emitted when start/end frames are marked
    save_interval_requested = Signal(str)  # Emitted when save interval is requested
    folder_selected = Signal(str)  # Emitted when a folder is selected
    save_folder_selected = Signal(str)  # Emitted when save folder is selected

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
        
        # Open folder button
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self._handle_open_folder)
        controls_layout.addWidget(self.open_folder_button)
        
        # Navigation buttons
        self.prev_button = QPushButton("Previous")
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self._handle_prev_file)
        controls_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Next")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self._handle_next_file)
        controls_layout.addWidget(self.next_button)
        
        # Current file label
        self.file_label = QLabel("No file selected")
        controls_layout.addWidget(self.file_label)
        
        layout.addLayout(controls_layout)
        
        # Frame controls
        frame_layout = QHBoxLayout()
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self._handle_slider_change)
        frame_layout.addWidget(self.slider)
        
        # Frame counter
        self.frame_label = QLabel("Frame: 0/0")
        frame_layout.addWidget(self.frame_label)
        
        # Autoplay button
        self.autoplay_button = QPushButton("Play")
        self.autoplay_button.setCheckable(True)
        self.autoplay_button.setEnabled(False)
        self.autoplay_button.clicked.connect(self._handle_autoplay_toggle)
        frame_layout.addWidget(self.autoplay_button)
        
        layout.addLayout(frame_layout)
        
        # Interval controls
        interval_layout = QHBoxLayout()
        
        # Start frame button
        self.start_frame_button = QPushButton("Mark Start")
        self.start_frame_button.setEnabled(False)
        self.start_frame_button.clicked.connect(self._handle_mark_start)
        interval_layout.addWidget(self.start_frame_button)
        
        # End frame button
        self.end_frame_button = QPushButton("Mark End")
        self.end_frame_button.setEnabled(False)
        self.end_frame_button.clicked.connect(self._handle_mark_end)
        interval_layout.addWidget(self.end_frame_button)
        
        # Save folder button
        self.save_folder_button = QPushButton("Set Save Folder")
        self.save_folder_button.clicked.connect(self._handle_set_save_folder)
        interval_layout.addWidget(self.save_folder_button)
        
        # Save interval button
        self.save_interval_button = QPushButton("Save Interval")
        self.save_interval_button.setEnabled(False)
        self.save_interval_button.clicked.connect(self._handle_save_interval)
        interval_layout.addWidget(self.save_interval_button)
        
        # Interval info label
        self.interval_label = QLabel("Interval: Not set")
        interval_layout.addWidget(self.interval_label)
        
        layout.addLayout(interval_layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Timer for autoplay
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # 100ms between frames (10 fps)
        
        # Store the current image display
        self.img_display = None
        
        # Store interval state
        self.start_frame = None
        self.end_frame = None
        
        # Store folder navigation state
        self.current_folder = None
        self.current_file_index = -1
        self.tiff_files = []
        
        # Store save folder
        self.save_folder = None

    @Slot()
    def _handle_open_folder(self):
        """Handle opening a folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        if folder_path:
            self.folder_selected.emit(folder_path)
            self._load_folder(folder_path)

    def _load_folder(self, folder_path):
        """Load TIFF files from the selected folder"""
        self.current_folder = folder_path
        self.tiff_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.tif', '.tiff'))]
        self.tiff_files.sort()  # Sort files alphabetically
        
        if self.tiff_files:
            self.current_file_index = 0
            self._load_current_file()
            self._update_navigation_buttons()
        else:
            self.current_file_index = -1
            self.file_label.setText("No TIFF files found")
            self._update_navigation_buttons()

    def _load_current_file(self):
        """Load the current file in the folder"""
        if 0 <= self.current_file_index < len(self.tiff_files):
            file_path = os.path.join(self.current_folder, self.tiff_files[self.current_file_index])
            self.file_label.setText(f"File: {self.tiff_files[self.current_file_index]}")
            self.file_selected.emit(file_path)
            
            # Don't reset interval state here - let the model handle it
            # The model will either load from JSON or reset if needed

    def _update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        self.prev_button.setEnabled(self.current_file_index > 0)
        self.next_button.setEnabled(self.current_file_index < len(self.tiff_files) - 1)

    @Slot()
    def _handle_prev_file(self):
        """Handle loading previous file"""
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self._load_current_file()
            self._update_navigation_buttons()

    @Slot()
    def _handle_next_file(self):
        """Handle loading next file"""
        if self.current_file_index < len(self.tiff_files) - 1:
            self.current_file_index += 1
            self._load_current_file()
            self._update_navigation_buttons()

    @Slot()
    def _handle_slider_change(self, value):
        """Internal slot to handle slider value changes"""
        self.frame_changed.emit(value)

    @Slot(bool)
    def _handle_autoplay_toggle(self, checked):
        """Internal slot to handle autoplay button toggle"""
        self.autoplay_toggled.emit(checked)

    @Slot(object)
    def show_image(self, image):
        """Display the given image using matplotlib"""
        if image is None:
            return
            
        if self.img_display is None:
            # First time: create the image display
            if len(image.shape) == 2:  # Grayscale
                self.img_display = self.ax.imshow(image, cmap='gray', aspect='equal')
            else:  # RGB
                self.img_display = self.ax.imshow(image, aspect='equal')
            self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        else:
            # Update existing image data
            self.img_display.set_data(image)
            if len(image.shape) == 2:  # Grayscale
                self.img_display.set_clim(vmin=image.min(), vmax=image.max())
            else:  # RGB
                # For RGB, we don't need to set clim as the values are already normalized
                pass
            
        # Force the canvas to update
        self.canvas.draw()

    @Slot(int, int)
    def update_frame_info(self, current, total):
        """Update the frame information display and slider position"""
        self.frame_label.setText(f"Frame: {current}/{total}")
        
        # Update slider position without triggering valueChanged
        self.slider.blockSignals(True)
        self.slider.setValue(current - 1)  # Convert to 0-based index
        self.slider.blockSignals(False)

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
        if self.img_display is not None:
            # Redraw the canvas to update image scaling while maintaining aspect ratio
            self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
            self.canvas.draw()

    @Slot(bool)
    def set_visible(self, visible):
        """Show or hide the window"""
        if visible:
            self.show()
        else:
            self.hide()

    @Slot(bool)
    def handle_stack_loaded(self, has_stack):
        """Handle stack loaded state"""
        if has_stack:
            self.slider.setEnabled(True)
            self.autoplay_button.setEnabled(True)
            self.start_frame_button.setEnabled(True)
            self.end_frame_button.setEnabled(True)
            self.img_display = None  # Reset image display for new stack
        else:
            self.slider.setEnabled(False)
            self.autoplay_button.setEnabled(False)
            self.start_frame_button.setEnabled(False)
            self.end_frame_button.setEnabled(False)
            self.save_interval_button.setEnabled(False)
            self.slider.setRange(0, 0)
            self.frame_label.setText("Frame: 0/0")
            self.interval_label.setText("Interval: Not set")
            self.start_frame = None
            self.end_frame = None

    @Slot()
    def _handle_mark_start(self):
        """Handle marking the start frame"""
        current_frame = self.slider.value()
        self.start_frame = current_frame
        self._update_interval_label()
        self._check_save_enabled()
        if self.end_frame is not None:
            self.interval_marked.emit(self.start_frame, self.end_frame)

    @Slot()
    def _handle_mark_end(self):
        """Handle marking the end frame"""
        current_frame = self.slider.value()
        self.end_frame = current_frame
        self._update_interval_label()
        self._check_save_enabled()
        if self.start_frame is not None:
            self.interval_marked.emit(self.start_frame, self.end_frame)

    @Slot()
    def _handle_set_save_folder(self):
        """Handle setting the save folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Save Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        if folder_path:
            self.save_folder = folder_path
            self.save_folder_selected.emit(folder_path)
            self.statusBar.showMessage(f"Save folder set to: {folder_path}")

    @Slot()
    def _handle_save_interval(self):
        """Handle saving the marked interval"""
        if self.save_folder is None:
            self.statusBar.showMessage("Please set a save folder first")
            return
            
        if self.current_file_index >= 0 and self.tiff_files:
            # Generate save filename based on current file
            current_file = self.tiff_files[self.current_file_index]
            base_name = os.path.splitext(current_file)[0]
            save_path = os.path.join(self.save_folder, f"{base_name}_trimmed.tif")
            self.save_interval_requested.emit(save_path)

    def _update_interval_label(self):
        """Update the interval label with current start/end frames"""
        if self.start_frame is not None and self.end_frame is not None:
            self.interval_label.setText(f"Interval: {self.start_frame + 1} - {self.end_frame + 1}")
        elif self.start_frame is not None:
            self.interval_label.setText(f"Start: {self.start_frame + 1}")
        elif self.end_frame is not None:
            self.interval_label.setText(f"End: {self.end_frame + 1}")
        else:
            self.interval_label.setText("Interval: Not set")

    def _check_save_enabled(self):
        """Enable/disable save button based on interval state"""
        self.save_interval_button.setEnabled(
            self.start_frame is not None and 
            self.end_frame is not None and
            self.start_frame != self.end_frame
        )

    @Slot(int, int)
    def update_interval_display(self, start_frame, end_frame):
        """Update the interval display with loaded values"""
        if start_frame == -1 and end_frame == -1:
            # No interval loaded
            self.start_frame = None
            self.end_frame = None
            self._update_interval_label()
            self._check_save_enabled()
            return
            
        self.start_frame = start_frame
        self.end_frame = end_frame
        self._update_interval_label()
        self._check_save_enabled() 