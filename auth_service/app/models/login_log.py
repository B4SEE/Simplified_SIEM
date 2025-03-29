from . import db, BaseModel

# Model to store login attempts for analysis
class LoginLog(db.Model, BaseModel):
    __tablename__ = 'login_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 can be up to 45 chars
    success = db.Column(db.Boolean, default=False, nullable=False)
    user_agent = db.Column(db.String(255))

    # Relationship
    user = db.relationship('User', back_populates='login_logs')

    def __repr__(self):
        status = "successful" if self.success else "failed"
        return f'<LoginLog {status} for user_id={self.user_id} at {self.created_at}>'
