"""Main controller module for the cell viewer application."""

from PySide6.QtCore import QObject, Slot
from ..services.PlaybackService import PlaybackService
from ..model.MainModel import MainModel
from ..view.MainView import MainView

class MainController(QObject):
    """Main controller for the cell viewer application."""
    
    def __init__(self):
        super().__init__()
        self.model = MainModel()
        self.view = MainView()
        self.playback = PlaybackService()
        
        # Connect model signals to view slots
        self.model.image_changed.connect(self.view.show_image)
        self.model.frame_info_changed.connect(self.view.update_frame_info)
        self.model.status_changed.connect(self.view.show_status_message)
        self.model.stack_loaded.connect(self.view.handle_stack_loaded)
        self.model.stack_loaded.connect(self._handle_stack_loaded)
        self.model.interval_loaded.connect(self.view.update_interval_display)
        
        # Connect view signals to model slots
        self.view.file_selected.connect(self.model.load_file)
        self.view.frame_changed.connect(self.model.set_current_frame)
        self.view.autoplay_toggled.connect(self._handle_playback_toggle)
        self.view.interval_marked.connect(self.model.set_interval)
        self.view.save_interval_requested.connect(self.model.save_interval)
        self.view.folder_selected.connect(self._handle_folder_selected)
        self.view.save_folder_selected.connect(self._handle_save_folder_selected)
        
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

    @Slot(bool)
    def _handle_playback_toggle(self, enabled):
        """Handle playback toggle from view"""
        if enabled:
            self.playback.start_playback()
        else:
            self.playback.stop_playback()
        self.view.set_autoplay_state(self.playback.is_playing())

    @Slot(bool)
    def _handle_stack_loaded(self, has_stack):
        """Handle stack loaded state"""
        if has_stack:
            min_frame, max_frame = self.model.get_frame_limits()
            self.view.set_slider_range(min_frame, max_frame)

    @Slot(str)
    def _handle_folder_selected(self, folder_path):
        """Handle folder selection"""
        self.model.status_changed.emit(f"Selected folder: {folder_path}")

    @Slot(str)
    def _handle_save_folder_selected(self, folder_path):
        """Handle save folder selection"""
        self.model.status_changed.emit(f"Save folder set to: {folder_path}")
