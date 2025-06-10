from . import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta

class User(db.Model, BaseModel):
    # User model for authentication and user management
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    account_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')
    login_logs = db.relationship('LoginLog', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, username, email, first_name=None, last_name=None):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def add_role(self, role):
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role):
        if role in self.roles:
            self.roles.remove(role)

    def record_login_attempt(self, success, ip_address, user_agent):
        """Record a login attempt and update user status accordingly."""
        if success:
            # Reset failed attempts on successful login
            self.failed_login_attempts = 0
            self.account_locked = False
        else:
            # Increment failed attempts
            self.failed_login_attempts += 1
            self.last_failed_login = datetime.utcnow()

            # Lock account after 5 failed attempts
            if self.failed_login_attempts >= 5:
                self.account_locked = True

        # Create login log entry
        log_entry = LoginLog(
            user_id=self.id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        db.session.add(log_entry)

    def is_locked(self):
        """Check if the account is locked."""
        if not self.account_locked:
            return False

        # If account was locked more than 30 minutes ago, unlock it
        if self.last_failed_login:
            unlock_time = datetime.utcnow() - timedelta(minutes=30)
            if self.last_failed_login < unlock_time:
                self.account_locked = False
                self.failed_login_attempts = 0
                return False

        return True

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'account_locked': self.account_locked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
