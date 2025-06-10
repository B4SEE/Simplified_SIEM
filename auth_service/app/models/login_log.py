from datetime import datetime
from . import db, BaseModel

# Model to store login attempts for analysis
class LoginLog(db.Model, BaseModel):
    __tablename__ = 'login_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 addresses can be up to 45 chars
    user_agent = db.Column(db.String(255))

    # Relationship
    user = db.relationship('User', back_populates='login_logs')

    def __init__(self, user=None, success=False, ip_address=None, user_agent=None, timestamp=None):
        if user:
            self.user_id = user.id
        self.success = success
        self.ip_address = ip_address or '0.0.0.0'
        self.user_agent = user_agent
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self):
        """Convert login log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'success': self.success,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

    def __repr__(self):
        status = "successful" if self.success else "failed"
        return f'<LoginLog {status} for user_id={self.user_id} at {self.timestamp}>'
