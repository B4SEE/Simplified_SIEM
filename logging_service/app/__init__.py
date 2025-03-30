# logging_service/app/__init__.py
from flask import Flask
from .models import db
from .models.log_entry import LogEntry
from .blueprints.api import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    db.init_app(app)
    app.register_blueprint(api_bp)
    return app