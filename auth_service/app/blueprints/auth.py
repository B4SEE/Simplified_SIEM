from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import check_password_hash
from ..models import db
from ..models.user import User
from ..models.login_log import LoginLog
from confluent_kafka import Producer
import json
import uuid

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Setup Kafka producer
def get_kafka_producer():
    conf = {
        'bootstrap.servers': current_app.config['KAFKA_BROKER'],
    }
    return Producer(conf)

@auth_bp.route('/status')
def status():
    """Simple endpoint to check if the auth service is running"""
    return jsonify({
        'status': 'Auth service is running',
        'service': 'auth'
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login requests"""
    data = request.json

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password', 'status': 'error'}), 400

    user = User.query.filter_by(username=data['username']).first()

    # Get IP address from request
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')

    # Authentication success or failure
    if user and user.verify_password(data['password']) and not user.is_locked():
        # Record successful login
        user.record_login_attempt(True, ip_address, user_agent)

        # Generate auth token (simplified for example)
        token = str(uuid.uuid4())

        # Publish login event to Kafka
        producer = get_kafka_producer()
        log_event = {
            'timestamp': str(db.func.now()),
            'ip_address': ip_address,
            'event_type': 'login_success',
            'user_ID': user.id,
            'user_agent': user_agent
        }
        producer.produce('logs', key=str(user.id), value=json.dumps(log_event))
        producer.flush()

        db.session.commit()
        return jsonify({
            'message': 'Login successful',
            'status': 'success',
            'token': token,
            'user_id': user.id
        })
    else:
        # Record failed login
        if user:
            user.record_login_attempt(False, ip_address, user_agent)
            db.session.commit()

        # Publish failed login event to Kafka
        producer = get_kafka_producer()
        log_event = {
            'timestamp': str(db.func.now()),
            'ip_address': ip_address,
            'event_type': 'login_failed',
            'user_ID': user.id if user else None,
            'user_agent': user_agent
        }
        producer.produce('logs', value=json.dumps(log_event))
        producer.flush()

        return jsonify({'message': 'Invalid credentials', 'status': 'error'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    """Handle user registration requests"""
    data = request.json

    # Validate required fields
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields', 'status': 'error'}), 400

    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists', 'status': 'error'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists', 'status': 'error'}), 400

    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', '')
    )
    new_user.password = data['password']  # This will use the password setter to hash

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    # Publish registration event to Kafka
    producer = get_kafka_producer()
    log_event = {
        'timestamp': str(db.func.now()),
        'ip_address': request.remote_addr,
        'event_type': 'user_registered',
        'user_ID': new_user.id,
        'user_agent': request.headers.get('User-Agent', '')
    }
    producer.produce('logs', key=str(new_user.id), value=json.dumps(log_event))
    producer.flush()

    return jsonify({
        'message': 'Registration successful',
        'status': 'success',
        'user_id': new_user.id
    }), 201
