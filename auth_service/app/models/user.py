from . import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta

class User(db.Model, BaseModel):
    # User model for authentication and user management
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    account_locked = db.Column(db.Boolean, default=False, nullable=False)
    account_locked_until = db.Column(db.DateTime)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')
    login_logs = db.relationship('LoginLog', back_populates='user', cascade='all, delete-orphan')

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

    def record_login_attempt(self, successful, ip_address, user_agent=None):
        from .login_log import LoginLog

        if successful:
            self.last_login_at = datetime.utcnow()
            self.failed_login_attempts = 0
            self.account_locked = False
            self.account_locked_until = None
        else:
            self.failed_login_attempts += 1
            # Lock account after 5 failed attempts
            if self.failed_login_attempts >= 5:
                self.account_locked = True
                self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)

        # Create login log entry
        log = LoginLog(
            user_id=self.id,
            ip_address=ip_address,
            success=successful,
            user_agent=user_agent
        )
        db.session.add(log)

    def is_locked(self):
        # Check if the account is currently locked
        if not self.account_locked:
            return False

        if self.account_locked_until and datetime.utcnow() > self.account_locked_until:
            # Auto-unlock if lock period has expired
            self.account_locked = False
            self.account_locked_until = None
            return False

        return True

    def __repr__(self):
        return f'<User {self.username}>'
