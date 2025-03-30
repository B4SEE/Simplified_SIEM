from flask import Blueprint, jsonify, request

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/status')
def status():
    """Simple endpoint to check if the auth service is running"""
    return jsonify({
        'status': 'Auth service is running',
        'service': 'auth'
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """Placeholder login endpoint"""
    return jsonify({
        'message': 'Login endpoint - to be implemented',
        'status': 'success'
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    """Placeholder registration endpoint"""
    return jsonify({
        'message': 'Registration endpoint - to be implemented',
        'status': 'success'
    })
