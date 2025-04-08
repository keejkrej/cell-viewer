"""Model module for the cell viewer application."""

from PySide6.QtCore import QObject, Signal, Slot
import numpy as np
from tifffile import imread

class Model(QObject):
    # Define signals
    image_changed = Signal(object)  # Emits the new image
    page_info_changed = Signal(int, int)  # Emits current and total pages
    status_changed = Signal(str)  # Emits status messages
    stack_loaded = Signal(bool)  # Emits when a stack is loaded or cleared

    def __init__(self):
        super().__init__()
        self.tiff_stack = None
        self.current_page = 0
        self.total_pages = 0
        self.file_path = None

    @Slot(str)
    def load_file(self, file_path):
        """Load a TIFF file and return success status"""
        try:
            self.tiff_stack = imread(file_path)
            if len(self.tiff_stack.shape) == 3:
                self.total_pages = self.tiff_stack.shape[0]
                self.current_page = 0
                self.file_path = file_path
                self.status_changed.emit(f"Loaded: {file_path}")
                self.stack_loaded.emit(True)
                self._update_view()
                return True
            else:
                self.status_changed.emit("Error: Not a valid TIFF stack")
                return False
        except Exception as e:
            self.status_changed.emit(f"Error loading file: {str(e)}")
            return False

    @Slot(int)
    def set_current_page(self, page):
        """Set the current page number"""
        if 0 <= page < self.total_pages:
            self.current_page = page
            self._update_view()
            return True
        return False

    def get_next_page(self):
        """Get the next page number (with wrapping)"""
        if self.tiff_stack is None:
            return None
        return (self.current_page + 1) % self.total_pages

    def has_stack(self):
        """Check if a valid stack is loaded"""
        return self.tiff_stack is not None

    def _update_view(self):
        """Update all view-related signals"""
        # Emit current image
        current_image = self._get_normalized_image()
        self.image_changed.emit(current_image)
        
        # Emit page info
        self.page_info_changed.emit(self.current_page + 1, self.total_pages)

    def _get_normalized_image(self):
        """Get the current page image, normalized to 8-bit"""
        if self.tiff_stack is None:
            return None
            
        image = self.tiff_stack[self.current_page]
        
        # Normalize to 0-255 if needed
        if image.dtype != np.uint8:
            image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
            
        return image

    def get_page_limits(self):
        """Get the minimum and maximum page numbers"""
        if self.tiff_stack is None:
            return 0, 0
        return 0, self.total_pages - 1 