from flask import Blueprint, request, jsonify
from ..log_ingester import KafkaProducerSingleton
from ..log_processor import LogProcessorSingleton
from ..models import db
from ..models.log_entry import LogEntry
from datetime import datetime, timedelta
from sqlalchemy import desc, func, case

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route('/logs', methods=['POST'])
def receive_logs():
    log_data = request.json
    kafka_producer = KafkaProducerSingleton()
    if not kafka_producer:
        return jsonify({"error": "Kafka producer not initialized"}), 500
    answer = kafka_producer.produce_log(log_data)
    if answer:
        message = "Log produced successfully"
    else:
        message = "Failed to produce logs"
    return jsonify({"message": message}), 200

@api_bp.route('/logs/search', methods=['GET'])
def search_logs():
    try:
        # --- AUTHORIZATION CHECK ---
        auth_header = request.headers.get('Authorization')
        user_id_header = request.headers.get('X-User-ID')
        user_role = request.headers.get('X-User-Role', 'user')  # Default to 'user' if not provided

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        if not user_id_header:
            return jsonify({'error': 'Missing X-User-ID header'}), 401

        # Only allow admins to see all logs; regular users can only see their own
        is_admin = user_role.lower() == 'admin'
        current_user_id = int(user_id_header)

        # --- EXISTING FILTERS ---
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        event_type = request.args.get('eventType')
        query_user_id = request.args.get('userId')
        severity = request.args.get('severity')
        limit = min(int(request.args.get('limit', 100)), 1000)  # Cap at 1000
        offset = int(request.args.get('offset', 0))

        query_obj = db.session.query(LogEntry)

        # Apply filters based on query parameters
        if start_date:
            query_obj = query_obj.filter(LogEntry.timestamp >= datetime.fromisoformat(start_date.replace('Z', '+00:00')))
        if end_date:
            query_obj = query_obj.filter(LogEntry.timestamp <= datetime.fromisoformat(end_date.replace('Z', '+00:00')))
        if event_type:
            query_obj = query_obj.filter(LogEntry.event_type == event_type)
        if severity:
            query_obj = query_obj.filter(LogEntry.severity == severity)

        # --- USER-BASED FILTERING ---
        if is_admin:
            # Admins can filter by userId if provided
            if query_user_id:
                query_obj = query_obj.filter(LogEntry.user_id == int(query_user_id))
        else:
            # Regular users can only see their own logs, ignore userId param
            query_obj = query_obj.filter(LogEntry.user_id == current_user_id)

        total = query_obj.count()
        logs = query_obj.order_by(desc(LogEntry.timestamp)).offset(offset).limit(limit).all()

        logs_data = [{
            'id': log.id,
            'timestamp': log.timestamp.isoformat(),
            'user_ID': log.user_id,
            'event_type': log.event_type,
            'ip_address': log.ip_address,
            'severity': log.severity or 'low',
            'geo': [float(log.latitude), float(log.longitude)] if log.latitude and log.longitude else None,
            'user_agent': log.user_agent,
            'additional_data': log.additional_data
        } for log in logs]

        return jsonify({
            'logs': logs_data,
            'total': total,
            'offset': offset,
            'limit': limit
        })

    except Exception as e:
        print(f"Error in search_logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/logs/stats', methods=['GET'])
def get_log_stats():
    try:
        # Get time range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)  # Default to last 7 days

        # Get query parameters
        start_date_param = request.args.get('startDate')
        end_date_param = request.args.get('endDate')

        if start_date_param:
            start_date = datetime.fromisoformat(start_date_param.replace('Z', '+00:00'))
        if end_date_param:
            end_date = datetime.fromisoformat(end_date_param.replace('Z', '+00:00'))

        # Query for stats
        stats = db.session.query(
            func.count().label('total'),
            func.sum(case((LogEntry.event_type == 'login_success', 1), else_=0)).label('successful_logins'),
            func.sum(case((LogEntry.event_type == 'login_failed', 1), else_=0)).label('failed_logins'),
            func.sum(case((LogEntry.severity == 'high', 1), else_=0)).label('alerts')
        ).filter(
            LogEntry.timestamp.between(start_date, end_date)
        ).first()

        # Get last login
        last_login = LogEntry.query.filter(
            LogEntry.event_type == 'login_success',
            LogEntry.timestamp.between(start_date, end_date)
        ).order_by(desc(LogEntry.timestamp)).first()

        return jsonify({
            'totalLogs': stats.total or 0,
            'successfulLogins': stats.successful_logins or 0,
            'failedLogins': stats.failed_logins or 0,
            'alertsCount': stats.alerts or 0,
            'lastLogin': last_login.timestamp.isoformat() if last_login else None
        })

    except Exception as e:
        print(f"Error in get_log_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/process_logs', methods=['POST'])
def process_logs_endpoint():
    log_processor = LogProcessorSingleton()
    if not log_processor:
        return jsonify({"error": "Log Processor Singleton not initialized"}), 500
    log_processor.consume_log()
    return jsonify({"message": "Logs processed"}), 200
