from flask import Blueprint, jsonify, request, g
from ..models import db
from ..models.login_log import LoginLog
from ..models.user import User
from .auth import token_required

logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')

@logs_bp.route('/search', methods=['GET'])
@token_required
def search_logs():
    """
    Search login logs with optional filters and include user roles for each log entry.
    Query params: user_id, limit, offset
    """
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', default=100, type=int)
    offset = request.args.get('offset', default=0, type=int)

    query = LoginLog.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    total = query.count()
    logs = query.order_by(LoginLog.timestamp.desc()).offset(offset).limit(limit).all()

    # Gather user_ids to batch-fetch roles
    user_ids = list(set(log.user_id for log in logs))
    users = User.query.filter(User.id.in_(user_ids)).all()
    user_roles_map = {u.id: [role.name for role in u.roles] for u in users}

    logs_data = []
    for log in logs:
        log_dict = log.to_dict()
        log_dict['roles'] = user_roles_map.get(log.user_id, [])
        logs_data.append(log_dict)

    return jsonify({
        'status': 'success',
        'total': total,
        'logs': logs_data
    })

@logs_bp.route('/', methods=['GET'])
@token_required
def get_logs():
    """
    Retrieve login logs with optional filters and include user roles for each log entry.
    Query params: user_id, limit, offset
    """
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)

    query = LoginLog.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    total = query.count()
    logs = query.order_by(LoginLog.timestamp.desc()).offset(offset).limit(limit).all()

    # Gather user_ids to batch-fetch roles
    user_ids = list(set(log.user_id for log in logs))
    users = User.query.filter(User.id.in_(user_ids)).all()
    user_roles_map = {u.id: [role.name for role in u.roles] for u in users}

    logs_data = []
    for log in logs:
        log_dict = log.to_dict()
        log_dict['roles'] = user_roles_map.get(log.user_id, [])
        logs_data.append(log_dict)

    return jsonify({
        'status': 'success',
        'total': total,
        'logs': logs_data
    })
