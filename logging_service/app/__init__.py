# logging_service/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config
from .models import db
from .models.log_entry import LogEntry
from .blueprints.api import api_bp
from .kafka_consumer import start_kafka_consumer_thread


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = False  # Disable auto-reload
    app.config['USE_RELOADER'] = False  # Disable auto-reload

    # Enable CORS for all routes
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-User-Id"]
        }
    })

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Create tables on startup
    with app.app_context():
        db.create_all()
        app.logger.info("Logging database tables created")

    start_kafka_consumer_thread()

    return app
