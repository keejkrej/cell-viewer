"""Model module for the cell viewer application."""

import numpy as np
from skimage.io import imread

class Model:
    def __init__(self):
        self.tiff_stack = None
        self.current_page = 0
        self.total_pages = 0
        self.file_path = None

    def load_file(self, file_path):
        """Load a TIFF file and return success status and message"""
        try:
            self.tiff_stack = imread(file_path)
            if len(self.tiff_stack.shape) == 3:
                self.total_pages = self.tiff_stack.shape[0]
                self.current_page = 0
                self.file_path = file_path
                return True, f"Loaded: {file_path}"
            else:
                return False, "Error: Not a valid TIFF stack"
        except Exception as e:
            return False, f"Error loading file: {str(e)}"

    def get_current_image(self):
        """Get the current page image, normalized to 8-bit"""
        if self.tiff_stack is None:
            return None
            
        image = self.tiff_stack[self.current_page]
        
        # Normalize to 0-255 if needed
        if image.dtype != np.uint8:
            image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
            
        return image

    def set_current_page(self, page):
        """Set the current page number"""
        if 0 <= page < self.total_pages:
            self.current_page = page
            return True
        return False

    def get_page_info(self):
        """Get current page information"""
        return {
            'current': self.current_page + 1,
            'total': self.total_pages,
            'file_path': self.file_path
        } 