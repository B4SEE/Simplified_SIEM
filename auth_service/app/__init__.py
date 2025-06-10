from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from .models import db

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, 
         resources={
             r"/*": {
                 "origins": ["http://localhost:3000"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "X-User-Id"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })

    @app.after_request
    def after_request(response):
        if request.method == 'OPTIONS':
            response = make_response()
            response.status_code = 200
        
        origin = request.headers.get('Origin')
        if origin == 'http://localhost:3000':
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-Id'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
        return response

    @app.errorhandler(500)
    def handle_500(error):
        response = make_response(jsonify({'message': 'Internal server error', 'status': 'error'}), 500)
        origin = request.headers.get('Origin')
        if origin == 'http://localhost:3000':
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-User-Id'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
        return response

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
