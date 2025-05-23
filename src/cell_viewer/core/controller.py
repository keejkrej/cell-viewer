"""Controller module for the cell viewer application."""

from PySide6.QtCore import QObject
from .service import PlaybackService
from .model import MainModel
from .view import MainView

class MainController(QObject):
    """Main controller for the cell viewer application."""
    
    def __init__(self):
        super().__init__()
        self.model = MainModel()
        self.view = MainView()
        self.playback = PlaybackService(self.model, self.view)
        
        # Connect model signals to view slots
        self.model.image_changed.connect(self.view.show_image)
        self.model.frame_info_changed.connect(self.view.update_frame_info)
        self.model.status_changed.connect(self.view.show_status_message)
        self.model.stack_loaded.connect(self.view.handle_stack_loaded)
        self.model.interval_loaded.connect(self.view.update_interval_display)
        
        # Connect view signals to model slots
        self.view.file_selected.connect(self.model.load_file)
        self.view.frame_changed.connect(self.model.set_current_frame)
        self.view.interval_marked.connect(self.model.set_interval)
        self.view.save_interval_requested.connect(self.model.save_interval)
        self.view.folder_selected.connect(self.model.set_current_folder)
        self.view.save_folder_selected.connect(self.model.set_save_folder)
        
        # Connect playback signals to model slots
        self.playback.request_advance.connect(self.model.advance_frame)
        
        # Show the view
        self.view.set_visible(True)

    def show(self):
        """Show the main window"""
        self.view.show()

    def close(self):
        """Close the main window"""
        self.view.close()