"""Controller module for the cell viewer application."""

from PySide6.QtCore import QObject
from ..model.Model import Model
from ..view.View import View
from .PlaybackController import PlaybackController

class Controller(QObject):
    def __init__(self):
        super().__init__()
        self.model = Model()
        self.view = View()
        self.playback = PlaybackController()
        
        # Connect playback controller to model
        self.playback.connect_model(self.model)
        
        # Connect View -> Model signals
        self.view.file_selected.connect(self.model.load_file)
        self.view.page_changed.connect(self.model.set_current_page)
        self.view.autoplay_toggled.connect(self.playback.set_playing)
        
        # Connect Model -> View signals
        self.model.image_changed.connect(self.view.show_image)
        self.model.page_info_changed.connect(self.view.update_page_info)
        self.model.status_changed.connect(self.view.show_status_message)
        
        # Connect PlaybackController -> View signals
        self.playback.state_changed.connect(self.view.set_autoplay_state)
        
        # Show the view
        self.view.set_visible(True)