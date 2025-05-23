"""Model module for the cell viewer application."""

from PySide6.QtCore import QObject, Signal, Slot
import numpy as np
import json
import os

class MainModel(QObject):
    # Define signals
    image_changed = Signal(np.ndarray)  # Emits the new image
    frame_info_changed = Signal(int, int)  # Emits current and total frames
    status_changed = Signal(str)  # Emits status messages
    stack_loaded = Signal(int, int)  # Emits min_frame, max_frame
    interval_loaded = Signal(int, int)  # Emits when interval is loaded from file

    def __init__(self):
        super().__init__()
        self.stack = None
        self.current_frame = 0
        self.total_frames = 0
        self.file_path = None
        self.start_frame = None
        self.end_frame = None
        self.current_folder = None
        self.save_folder = None

    def _get_interval_path(self):
        """Get the path to the interval JSON file"""
        if self.file_path is None:
            raise ValueError("No file path set")
        return os.path.splitext(self.file_path)[0] + '_interval.json'

    def _load_interval(self):
        """Load interval from JSON file"""
        try:
            interval_file = self._get_interval_path()
            if not os.path.exists(interval_file):
                raise FileNotFoundError(f"Interval file not found: {interval_file}")
            with open(interval_file, 'r') as f:
                data = json.load(f)
                self.start_frame = data.get('start_frame')
                self.end_frame = data.get('end_frame')
                if self.start_frame is not None and self.end_frame is not None:
                    self.interval_loaded.emit(self.start_frame, self.end_frame)
        except Exception as e:
            self.status_changed.emit(f"Error loading interval: {str(e)}")
            self.interval_loaded.emit(-1, -1)

    def _save_interval(self):
        """Save interval to JSON file"""
        try:
            interval_file = self._get_interval_path()
            with open(interval_file, 'w') as f:
                json.dump({
                    'start_frame': self.start_frame,
                    'end_frame': self.end_frame
                }, f, indent=4)
            return True
        except Exception as e:
            self.status_changed.emit(f"Error saving interval: {str(e)}")
            return False

    def _update_view(self):
        """Update all view-related signals"""
        try:
            # Emit current image
            current_image = self.stack[self.current_frame] # (c, h, w)
            self.image_changed.emit(current_image)
            
            # Emit frame info
            self.frame_info_changed.emit(self.current_frame + 1, self.total_frames)
        except Exception as e:
            self.status_changed.emit(f"Error updating view: {str(e)}")

    @Slot(int, int)
    def set_interval(self, start_frame, end_frame):
        """Set the interval for saving"""
        try:
            if 0 <= start_frame < self.total_frames and 0 <= end_frame < self.total_frames:
                self.start_frame = min(start_frame, end_frame)
                self.end_frame = max(start_frame, end_frame)
                self._save_interval()  # Save interval to file
                self.status_changed.emit(f"Interval set: {self.start_frame + 1} - {self.end_frame + 1}")
            else:
                self.status_changed.emit(f"Error: Invalid interval: {start_frame} - {end_frame}")
        except Exception as e:
            self.status_changed.emit(f"Error setting interval: {str(e)}")

    @Slot(str)
    def save_interval(self, file_path):
        """Save the marked interval to a new TIFF file"""
        try:
            if self.stack is None or self.start_frame is None or self.end_frame is None:
                self.status_changed.emit("Error: No interval marked or no stack loaded")
                return
            # Extract the interval from the stack
            interval_stack = self.stack[self.start_frame:self.end_frame + 1]
            
            # Save to new file
            np.save(file_path, interval_stack)
            self.status_changed.emit(f"Saved interval to {file_path}")
        except Exception as e:
            self.status_changed.emit(f"Error saving interval: {str(e)}")

    @Slot(str)
    def load_file(self, file_path):
        """Load a TIFF file and return success status"""
        try:
            self.stack = np.load(file_path) # (num_frames, c, h, w)
            if len(self.stack.shape) != 4 or self.stack.shape[1] != 3:
                self.status_changed.emit("Error: Not a valid pattern, nuclei, cyto stack")
                self.stack_loaded.emit(-1, -1)
                return
            self.total_frames = self.stack.shape[0]
            self.current_frame = 0
            self.file_path = file_path
            self.status_changed.emit(f"Loaded stack: {file_path}")
            self.stack_loaded.emit(0, self.total_frames - 1)
            # Reset interval state before trying to load
            self.start_frame = None
            self.end_frame = None
            self._load_interval()
            self._update_view()
        except Exception as e:
            self.status_changed.emit(f"Error loading file: {str(e)}")
            self.stack_loaded.emit(-1, -1)
            
    @Slot(int)
    def set_current_frame(self, frame):
        """Set the current frame number"""
        try:
            if 0 <= frame < self.total_frames:
                self.current_frame = frame
                self._update_view()
            else:
                self.status_changed.emit(f"Frame number out of range: {frame}")
        except Exception as e:
            self.status_changed.emit(f"Error setting frame: {str(e)}")

    @Slot()
    def advance_frame(self):
        """Handle frame advancement signal"""
        try:
            self.set_current_frame(self.current_frame + 1)
        except Exception as e:
            self.status_changed.emit(f"Error advancing frame: {str(e)}")

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