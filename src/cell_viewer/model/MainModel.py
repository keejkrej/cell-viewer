"""Model module for the cell viewer application."""

from PySide6.QtCore import QObject, Signal, Slot
import numpy as np
from tifffile import imread

class MainModel(QObject):
    # Define signals
    image_changed = Signal(object)  # Emits the new image
    frame_info_changed = Signal(int, int)  # Emits current and total frames
    status_changed = Signal(str)  # Emits status messages
    stack_loaded = Signal(bool)  # Emits when a stack is loaded or cleared

    def __init__(self):
        super().__init__()
        self.tiff_stack = None
        self.current_frame = 0
        self.total_frames = 0
        self.file_path = None

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
                self.stack_loaded.emit(True)
                self._update_view()
                return True
            elif len(self.tiff_stack.shape) == 4:
                # RGB stack: [frames, height, width, channels]
                if self.tiff_stack.shape[3] == 3:  # Check for RGB channels
                    self.total_frames = self.tiff_stack.shape[0]
                    self.current_frame = 0
                    self.file_path = file_path
                    self.status_changed.emit(f"Loaded RGB stack: {file_path}")
                    self.stack_loaded.emit(True)
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
            
        image = self.tiff_stack[self.current_frame]
        
        # Handle both grayscale and RGB images
        if len(image.shape) == 2:  # Grayscale
            if image.dtype != np.uint8:
                image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
        elif len(image.shape) == 3:  # RGB
            if image.dtype != np.uint8:
                # Normalize each channel independently
                for i in range(3):
                    channel = image[:,:,i]
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