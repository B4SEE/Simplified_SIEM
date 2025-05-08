from flask import Flask
from .models import db

def create_app(config_name='default'):
    app = Flask(__name__)

    # Load configuration
    from .config import Config
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.alarms import alarms_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(alarms_bp)

    # Ensure all models are imported
    from .models.user import User
    from .models.role import Role
    from .models.login_log import LoginLog
    from .models.alarm import Alarm

    # Create all tables when the app starts
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")

    return app
