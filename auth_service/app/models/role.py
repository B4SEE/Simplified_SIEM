from . import db, BaseModel

# Role model for user permissions
class Role(db.Model, BaseModel):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    # Many-to-many relationship with users through user_roles
    users = db.relationship('User', secondary='user_roles', back_populates='roles')

    def __repr__(self):
        return f'<Role {self.name}>'

# Association table for many-to-many relationship between User and Role
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=db.func.now(), nullable=False)
)
