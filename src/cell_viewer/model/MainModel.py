"""Model module for the cell viewer application."""

from PySide6.QtCore import QObject, Signal, Slot
import numpy as np
from imageio.v3 import imread, imwrite
import json
import os

class MainModel(QObject):
    # Define signals
    image_changed = Signal(object)  # Emits the new image
    frame_info_changed = Signal(int, int)  # Emits current and total frames
    status_changed = Signal(str)  # Emits status messages
    stack_loaded = Signal(bool, int, int)  # Emits has_stack, min_frame, max_frame
    interval_loaded = Signal(int, int)  # Emits when interval is loaded from file

    def __init__(self):
        super().__init__()
        self.tiff_stack = None
        self.current_frame = 0
        self.total_frames = 0
        self.file_path = None
        self.start_frame = None
        self.end_frame = None
        self.current_folder = None
        self.save_folder = None

    def _get_interval_file_path(self):
        """Get the path to the interval JSON file"""
        if self.file_path is None:
            return None
        return os.path.splitext(self.file_path)[0] + '_interval.json'

    def _load_interval(self):
        """Load interval from JSON file"""
        interval_file = self._get_interval_file_path()
        if interval_file and os.path.exists(interval_file):
            try:
                with open(interval_file, 'r') as f:
                    data = json.load(f)
                    self.start_frame = data.get('start_frame')
                    self.end_frame = data.get('end_frame')
                    if self.start_frame is not None and self.end_frame is not None:
                        self.interval_loaded.emit(self.start_frame, self.end_frame)
                        return True
            except Exception as e:
                self.status_changed.emit(f"Error loading interval: {str(e)}")
        return False

    def _save_interval(self):
        """Save interval to JSON file"""
        if self.file_path is None or self.start_frame is None or self.end_frame is None:
            return False
            
        interval_file = self._get_interval_file_path()
        try:
            with open(interval_file, 'w') as f:
                json.dump({
                    'start_frame': self.start_frame,
                    'end_frame': self.end_frame
                }, f, indent=4)
            return True
        except Exception as e:
            self.status_changed.emit(f"Error saving interval: {str(e)}")
            return False

    @Slot(int, int)
    def set_interval(self, start_frame, end_frame):
        """Set the interval for saving"""
        if 0 <= start_frame < self.total_frames and 0 <= end_frame < self.total_frames:
            self.start_frame = min(start_frame, end_frame)
            self.end_frame = max(start_frame, end_frame)
            self._save_interval()  # Save interval to file
            self.status_changed.emit(f"Interval set: {self.start_frame + 1} - {self.end_frame + 1}")
            return True
        return False

    @Slot(str)
    def save_interval(self, file_path):
        """Save the marked interval to a new TIFF file"""
        if self.tiff_stack is None or self.start_frame is None or self.end_frame is None:
            self.status_changed.emit("Error: No interval marked or no stack loaded")
            return False

        try:
            # Extract the interval from the stack
            interval_stack = self.tiff_stack[self.start_frame:self.end_frame + 1]
            
            # Save to new file
            imwrite(file_path, interval_stack)
            self.status_changed.emit(f"Saved interval to {file_path}")
            return True
        except Exception as e:
            self.status_changed.emit(f"Error saving interval: {str(e)}")
            return False

    @Slot(str)
    def load_file(self, file_path):
        """Load a TIFF file and return success status"""
        try:
            self.tiff_stack = imread(file_path)
            # Handle different stack types
            if len(self.tiff_stack.shape) == 3:
                # Grayscale stack: [frames, height, width]
                self.total_frames = self.tiff_stack.shape[0]
                self.current_frame = 0
                self.file_path = file_path
                self.status_changed.emit(f"Loaded grayscale stack: {file_path}")
                min_frame, max_frame = self.get_frame_limits()
                self.stack_loaded.emit(True, min_frame, max_frame)
                # Reset interval state before trying to load
                self.start_frame = None
                self.end_frame = None
                if not self._load_interval():  # If no interval file exists
                    self.interval_loaded.emit(-1, -1)  # Signal that no interval was loaded
                self._update_view()
                return True
            elif len(self.tiff_stack.shape) == 4:
                # RGB stack: [frames, height, width, channels]
                if self.tiff_stack.shape[3] == 3:  # Check for RGB channels
                    self.total_frames = self.tiff_stack.shape[0]
                    self.current_frame = 0
                    self.file_path = file_path
                    self.status_changed.emit(f"Loaded RGB stack: {file_path}")
                    min_frame, max_frame = self.get_frame_limits()
                    self.stack_loaded.emit(True, min_frame, max_frame)
                    # Reset interval state before trying to load
                    self.start_frame = None
                    self.end_frame = None
                    if not self._load_interval():  # If no interval file exists
                        self.interval_loaded.emit(-1, -1)  # Signal that no interval was loaded
                    self._update_view()
                    return True
                else:
                    self.status_changed.emit("Error: Unsupported number of color channels")
                    return False
            else:
                self.status_changed.emit("Error: Not a valid TIFF stack")
                return False
        except Exception as e:
            self.status_changed.emit(f"Error loading file: {str(e)}")
            return False

    @Slot(int)
    def set_current_frame(self, frame):
        """Set the current frame number"""
        if 0 <= frame < self.total_frames:
            self.current_frame = frame
            self._update_view()
            return True
        return False

    def get_next_frame(self):
        """Get the next frame number (with wrapping)"""
        if self.tiff_stack is None:
            return None
        return (self.current_frame + 1) % self.total_frames

    def has_stack(self):
        """Check if a valid stack is loaded"""
        return self.tiff_stack is not None

    def _update_view(self):
        """Update all view-related signals"""
        # Emit current image
        current_image = self._get_normalized_image()
        self.image_changed.emit(current_image)
        
        # Emit frame info
        self.frame_info_changed.emit(self.current_frame + 1, self.total_frames)

    def _get_normalized_image(self):
        """Get the current frame image, normalized to 8-bit"""
        if self.tiff_stack is None:
            return None
            
        image = np.copy(self.tiff_stack[self.current_frame])
        
        # Handle both grayscale and RGB images
        if len(image.shape) == 2:  # Grayscale
            if image.max() == image.min():
                image = np.zeros_like(image)
            else:
                image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
        elif len(image.shape) == 3:  # RGB
            # Normalize each channel independently
            for i in range(3):
                channel = image[:,:,i]
                if channel.max() == channel.min():
                    image[:,:,i] = np.zeros_like(channel)
                else:
                    image[:,:,i] = ((channel - channel.min()) / (channel.max() - channel.min()) * 255).astype(np.uint8)
            
        return image

    def get_frame_limits(self):
        """Get the minimum and maximum frame numbers"""
        if self.tiff_stack is None:
            return 0, 0
        return 0, self.total_frames - 1

    @Slot()
    def advance_frame(self):
        """Handle frame advancement signal"""
        if self.has_stack():
            next_frame = self.get_next_frame()
            if next_frame is not None:
                self.set_current_frame(next_frame)

    @Slot(str)
    def set_current_folder(self, folder_path):
        """Set the current folder and update status"""
        self.current_folder = folder_path
        self.status_changed.emit(f"Selected folder: {folder_path}")

    @Slot(str)
    def set_save_folder(self, folder_path):
        """Set the save folder and update status"""
        self.save_folder = folder_path
        self.status_changed.emit(f"Save folder set to: {folder_path}") 