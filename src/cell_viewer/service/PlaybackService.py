"""Service for handling video playback functionality."""

from PySide6.QtCore import QObject, Slot, QTimer, Signal

class PlaybackService(QObject):
    """Service for handling video playback functionality."""
    
    # Define signals
    frame_advance_requested = Signal()  # Signal to request frame advancement
    autoplay_state_changed = Signal(bool)  # Signal to update autoplay state
    
    def __init__(self):
        """
        Initialize the playback service.
        """
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._request_advance)
        self.playback_speed = 100  # Default speed in milliseconds

    # =====================================================================
    # Private Methods
    # =====================================================================

    def _start_playback(self):
        """Start the playback timer"""
        self.timer.start(self.playback_speed)
        
    def _stop_playback(self):
        """Stop the playback timer"""
        self.timer.stop()
        
    def _set_playback_speed(self, speed_ms):
        """Set the playback speed in milliseconds"""
        self.playback_speed = speed_ms
        if self.timer.isActive():
            self.timer.setInterval(speed_ms)
            
    def _is_playing(self):
        """Check if playback is currently active"""
        return self.timer.isActive()
        
    @Slot()
    def _request_advance(self):
        """Handle timer timeout by requesting frame advancement"""
        self.frame_advance_requested.emit()
        
    # =====================================================================
    # Public Methods
    # =====================================================================

    @Slot(bool)
    def handle_playback_toggle(self, enabled):
        """Handle playback toggle from view"""
        if enabled:
            self._start_playback()
        else:
            self._stop_playback()
        self.autoplay_state_changed.emit(self._is_playing()) 