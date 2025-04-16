"""Service for handling video playback functionality."""

from PySide6.QtCore import QObject, Signal, Slot, QTimer

class PlaybackService(QObject):
    """Service for handling video playback functionality."""
    
    # Define signals
    request_advance = Signal()  # Signal to request frame advancement
    
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._request_advance)
        self.playback_speed = 100  # Default speed in milliseconds
        
    def start_playback(self):
        """Start the playback timer"""
        self.timer.start(self.playback_speed)
        
    def stop_playback(self):
        """Stop the playback timer"""
        self.timer.stop()
        
    def set_playback_speed(self, speed_ms):
        """Set the playback speed in milliseconds"""
        self.playback_speed = speed_ms
        if self.timer.isActive():
            self.timer.setInterval(speed_ms)
            
    def is_playing(self):
        """Check if playback is currently active"""
        return self.timer.isActive()
        
    @Slot()
    def _request_advance(self):
        """Handle timer timeout by requesting frame advancement"""
        self.request_advance.emit() 