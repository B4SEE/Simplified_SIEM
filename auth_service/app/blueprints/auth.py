from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import db
from ..models.user import User
from ..models.login_log import LoginLog
from confluent_kafka import Producer
import json
import uuid
import re
from functools import wraps
import sys

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Setup Kafka producer
def get_kafka_producer():
    conf = {
        'bootstrap.servers': current_app.config['KAFKA_BROKER'],
    }
    return Producer(conf)

# Authentication middleware
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Special test-mode bypass for unit testing
        # This allows tests to set a test user ID directly
        if request.headers.get('X-Test-Mode') == 'true' and request.headers.get('X-Test-User-ID'):
            user_id = request.headers.get('X-Test-User-ID')
            user = User.query.get(user_id)
            if not user:
                return jsonify({'message': 'Test user not found', 'status': 'error'}), 401
            g.user = user
            return f(*args, **kwargs)

        # Regular auth token validation
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'message': 'Invalid or missing token', 'status': 'error'}), 401

        # Strip "Bearer " prefix
        token = token.split('Bearer ')[1]

        # In production, validate JWT token here
        # For now, we'll just validate UUID format and look up the user
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', token):
            return jsonify({'message': 'Invalid token format', 'status': 'error'}), 401

        # For this demo, look up user via session instead of JWT claims
        # In production, decode JWT and verify signature
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'message': 'User ID not provided', 'status': 'error'}), 401

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({'message': 'User not found', 'status': 'error'}), 401

        g.user = user
        return f(*args, **kwargs)
    return decorated

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
        print('📣 [AUTH SERVICE] Produced login_failed event to Kafka', flush=True)


        return jsonify({'message': 'Invalid credentials', 'status': 'error'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    """Enhanced user registration with more comprehensive form"""
    data = request.json

    # Validate required fields
    required_fields = ['username', 'email', 'password', 'confirm_password']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields', 'status': 'error'}), 400

    # Validate email format
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, data['email']):
        return jsonify({'message': 'Invalid email format', 'status': 'error'}), 400

    # Validate password strength
    if len(data['password']) < 8:
        return jsonify({'message': 'Password must be at least 8 characters', 'status': 'error'}), 400

    # Verify passwords match
    if data['password'] != data['confirm_password']:
        return jsonify({'message': 'Passwords do not match', 'status': 'error'}), 400

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
        last_name=data.get('last_name', ''),
        # Add any additional fields you want to capture
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

    # In a real implementation, you would send an email verification here
    # For now, we'll just log that it would happen
    current_app.logger.info(f"Would send verification email to {new_user.email}")

    return jsonify({
        'message': 'Registration successful. Please check your email to verify your account.',
        'status': 'success',
        'user_id': new_user.id
    }), 201

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get the current user's profile information"""
    user = g.user

    return jsonify({
        'status': 'success',
        'profile': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None
        }
    })

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update the current user's profile information"""
    user = g.user
    data = request.json

    if not data:
        return jsonify({'message': 'No update data provided', 'status': 'error'}), 400

    # Track what fields were updated for logging
    updated_fields = []

    # Update username if provided and not already taken
    if 'username' in data and data['username'] != user.username:
        if User.query.filter(User.id != user.id, User.username == data['username']).first():
            return jsonify({'message': 'Username already taken', 'status': 'error'}), 400
        user.username = data['username']
        updated_fields.append('username')

    # Update email if provided and not already taken
    if 'email' in data and data['email'] != user.email:
        # Validate email format
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'message': 'Invalid email format', 'status': 'error'}), 400

        if User.query.filter(User.id != user.id, User.email == data['email']).first():
            return jsonify({'message': 'Email already taken', 'status': 'error'}), 400

        user.email = data['email']
        updated_fields.append('email')

        # In a real implementation, you would require email verification here

    # Update name fields if provided
    if 'first_name' in data and data['first_name'] != user.first_name:
        user.first_name = data['first_name']
        updated_fields.append('first_name')

    if 'last_name' in data and data['last_name'] != user.last_name:
        user.last_name = data['last_name']
        updated_fields.append('last_name')

    # If no fields were updated, return early
    if not updated_fields:
        return jsonify({'message': 'No changes detected', 'status': 'success'})

    # Save changes to database
    db.session.commit()

    # Log the profile update
    producer = get_kafka_producer()
    log_event = {
        'timestamp': str(db.func.now()),
        'ip_address': request.remote_addr,
        'event_type': 'profile_updated',
        'user_ID': user.id,
        'user_agent': request.headers.get('User-Agent', ''),
        'updated_fields': updated_fields
    }
    producer.produce('logs', key=str(user.id), value=json.dumps(log_event))
    producer.flush()

    return jsonify({
        'message': 'Profile updated successfully',
        'status': 'success',
        'updated_fields': updated_fields
    })

@auth_bp.route('/password', methods=['PUT'])
@token_required
def change_password():
    """Change the current user's password"""
    user = g.user
    data = request.json

    if not data or not all(k in data for k in ['current_password', 'new_password', 'confirm_password']):
        return jsonify({'message': 'Missing required fields', 'status': 'error'}), 400

    # Verify current password
    if not user.verify_password(data['current_password']):
        return jsonify({'message': 'Current password is incorrect', 'status': 'error'}), 401

    # Verify new password meets requirements
    if len(data['new_password']) < 8:
        return jsonify({'message': 'New password must be at least 8 characters', 'status': 'error'}), 400

    # Verify new passwords match
    if data['new_password'] != data['confirm_password']:
        return jsonify({'message': 'New passwords do not match', 'status': 'error'}), 400

    # Update password
    user.password = data['new_password']
    db.session.commit()

    # Log the password change
    producer = get_kafka_producer()
    log_event = {
        'timestamp': str(db.func.now()),
        'ip_address': request.remote_addr,
        'event_type': 'password_changed',
        'user_ID': user.id,
        'user_agent': request.headers.get('User-Agent', '')
    }
    producer.produce('logs', key=str(user.id), value=json.dumps(log_event))
    producer.flush()

    return jsonify({
        'message': 'Password updated successfully',
        'status': 'success'
    })

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify a user's email address using a token"""
    # In a real implementation, you would validate the token and update the user's email verification status
    # For this example, we'll just return a success message

    return jsonify({
        'message': 'Email verified successfully',
        'status': 'success'
    })
