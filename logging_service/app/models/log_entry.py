# logging_service/app/models/log_entry.py
from . import db, BaseModel

# Model for storing authentication and security event logs
class LogEntry(db.Model, BaseModel):
    __tablename__ = 'log_entries'

    id = db.Column(db.Integer, primary_key=True)
    # Timestamp when the event occurred (may differ from record creation time)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)  # IPv6 can be up to 45 chars
    event_type = db.Column(db.String(50), nullable=False, index=True)  # login_success, login_failed, etc.
    user_id = db.Column(db.Integer, index=True)  # No foreign key since this is a separate service

    # Store geographical coordinates separately for better query performance
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    user_agent = db.Column(db.String(255))
    severity = db.Column(db.String(20))  # low, medium, high
    additional_data = db.Column(db.JSON)  # For any extra event-specific data

    def __repr__(self):
        return f'<LogEntry {self.event_type} for user_id={self.user_id} at {self.timestamp}>'

    @property
    def geo(self):
        """Return geographical coordinates as a tuple for compatibility with analyzer."""
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        return None

    @geo.setter
    def geo(self, coordinates):
        """Set geographical coordinates from a tuple."""
        if coordinates and len(coordinates) == 2:
            self.latitude, self.longitude = coordinates
