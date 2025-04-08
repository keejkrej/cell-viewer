"""Controller module for the cell viewer application."""

from ..model.model import Model
from ..view.view import View

class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View()
        
        # Connect signals
        self.view.open_button.clicked.connect(self.handle_open_file)
        self.view.slider.valueChanged.connect(self.handle_slider_change)
        
    def handle_open_file(self):
        """Handle file open button click"""
        file_path = self.view.get_file_path()
        if file_path:
            success, message = self.model.load_file(file_path)
            self.view.show_status_message(message)
            
            if success:
                self.view.set_slider_range(0, self.model.total_pages - 1)
                self.update_display()
    
    def handle_slider_change(self, value):
        """Handle slider value change"""
        if self.model.set_current_page(value):
            self.update_display()
    
    def update_display(self):
        """Update the display with current image and page info"""
        # Update image
        current_image = self.model.get_current_image()
        self.view.show_image(current_image)
        
        # Update page info
        page_info = self.model.get_page_info()
        self.view.update_page_info(page_info['current'], page_info['total'])
    
    def show(self):
        """Show the main window"""
        self.view.show() 