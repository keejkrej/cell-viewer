"""Playback controller module for the cell viewer application."""

from PySide6.QtCore import QObject, Signal, Slot, QTimer

class PlaybackController(QObject):
    # Define signals
    state_changed = Signal(bool)  # Emits when playback state changes

    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # 100ms between frames (10 fps)
        self.model = None
        self.is_playing = False
        
    def connect_model(self, model):
        """Connect to model for page advancement"""
        self.model = model
        self.timer.timeout.connect(self._advance_page)
        self.model.stack_loaded.connect(self._handle_stack_state)
        
    @Slot(bool)
    def set_playing(self, enabled):
        """Start or stop playback"""
        self.is_playing = enabled
        if enabled and self.model and self.model.has_stack():
            self.timer.start()
        else:
            self.timer.stop()
        self.state_changed.emit(enabled and self.model and self.model.has_stack())
        
    @Slot(bool)
    def _handle_stack_state(self, has_stack):
        """Handle stack load/unload"""
        if not has_stack and self.is_playing:
            self.set_playing(False)
        
    def _advance_page(self):
        """Advance to the next page during playback"""
        if self.model and self.model.has_stack():
            next_page = self.model.get_next_page()
            if next_page is not None:
                self.model.set_current_page(next_page) 