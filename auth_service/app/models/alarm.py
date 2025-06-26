from . import db, BaseModel

class Alarm(db.Model, BaseModel):
    """Model for configurable security alarms"""
    __tablename__ = 'alarms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    event_type = db.Column(db.String(50), nullable=False)  # login_failed, unusual_login_location, etc.
    threshold = db.Column(db.Integer, default=5)  # Number of events to trigger alarm
    time_window = db.Column(db.Integer, default=60)  # Time window in minutes
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Additional criteria stored as JSON
    criteria = db.Column(db.JSON)

    # Relationship
    user = db.relationship('User', backref=db.backref('alarms', lazy=True))

    def __repr__(self):
        status = "active" if self.is_active else "disabled"
        return f'<Alarm {self.name} ({status})>'

    def to_dict(self):
        """Convert alarm to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'event_type': self.event_type,
            'threshold': self.threshold,
            'time_window': self.time_window,
            'is_active': self.is_active,
            'severity': self.severity,
            'criteria': self.criteria,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
