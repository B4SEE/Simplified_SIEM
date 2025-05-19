from flask import Blueprint, jsonify, request, current_app, g
from ..models import db
from ..models.alarm import Alarm
from .auth import token_required, get_kafka_producer
import json
from datetime import datetime

alarms_bp = Blueprint('alarms', __name__, url_prefix='/api/alarms')

@alarms_bp.route('/', methods=['GET'])
@token_required
def get_alarms():
    """Get all alarms for the current user"""
    user = g.user

    # Check if user has admin role to see all alarms
    if user.has_role('admin'):
        alarms = Alarm.query.all()
    else:
        alarms = Alarm.query.filter_by(user_id=user.id).all()

    result = [alarm.to_dict() for alarm in alarms]

    return jsonify({
        'status': 'success',
        'count': len(result),
        'alarms': result
    })

@alarms_bp.route('/<int:alarm_id>', methods=['GET'])
@token_required
def get_alarm(alarm_id):
    """Get a specific alarm"""
    user = g.user

    alarm = Alarm.query.get_or_404(alarm_id)

    # Check if user has permission to view this alarm
    if not user.has_role('admin') and alarm.user_id != user.id:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to view this alarm'
        }), 403

    return jsonify({
        'status': 'success',
        'alarm': alarm.to_dict()
    })

@alarms_bp.route('/', methods=['POST'])
@token_required
def create_alarm():
    """Create a new alarm"""
    user = g.user
    data = request.json

    # Validate required fields
    required_fields = ['name', 'event_type']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400

    new_alarm = Alarm(
        name=data['name'],
        description=data.get('description', ''),
        event_type=data['event_type'],
        threshold=data.get('threshold', 5),
        time_window=data.get('time_window', 60),
        is_active=data.get('is_active', True),
        severity=data.get('severity', 'medium'),
        criteria=data.get('criteria', {}),
        user_id=user.id
    )

    db.session.add(new_alarm)
    db.session.commit()

    # Log the alarm creation event
    producer = get_kafka_producer()
    log_event = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr,
        'event_type': 'alarm_created',
        'user_ID': user.id,
        'user_agent': request.headers.get('User-Agent', ''),
        'alarm_id': new_alarm.id,
        'alarm_name': new_alarm.name
    }
    producer.produce('logs', key=str(user.id), value=json.dumps(log_event))
    producer.flush()

    return jsonify({
        'status': 'success',
        'message': 'Alarm created successfully',
        'alarm_id': new_alarm.id,
        'alarm': new_alarm.to_dict()
    }), 201

@alarms_bp.route('/<int:alarm_id>', methods=['PUT'])
@token_required
def update_alarm(alarm_id):
    """Update an existing alarm"""
    user = g.user
    data = request.json

    alarm = Alarm.query.get_or_404(alarm_id)

    # Check if user has permission to update this alarm
    if not user.has_role('admin') and alarm.user_id != user.id:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to update this alarm'
        }), 403

    # Track updated fields for logging
    updated_fields = []

    # Update fields
    if 'name' in data and data['name'] != alarm.name:
        alarm.name = data['name']
        updated_fields.append('name')

    if 'description' in data and data['description'] != alarm.description:
        alarm.description = data['description']
        updated_fields.append('description')

    if 'event_type' in data and data['event_type'] != alarm.event_type:
        alarm.event_type = data['event_type']
        updated_fields.append('event_type')

    if 'threshold' in data and data['threshold'] != alarm.threshold:
        alarm.threshold = data['threshold']
        updated_fields.append('threshold')

    if 'time_window' in data and data['time_window'] != alarm.time_window:
        alarm.time_window = data['time_window']
        updated_fields.append('time_window')

    if 'is_active' in data and data['is_active'] != alarm.is_active:
        alarm.is_active = data['is_active']
        updated_fields.append('is_active')

    if 'severity' in data and data['severity'] != alarm.severity:
        alarm.severity = data['severity']
        updated_fields.append('severity')

    if 'criteria' in data and data['criteria'] != alarm.criteria:
        alarm.criteria = data['criteria']
        updated_fields.append('criteria')

    # If no fields were updated, return early
    if not updated_fields:
        return jsonify({
            'status': 'success',
            'message': 'No changes detected'
        })

    db.session.commit()

    # Log the alarm update event
    producer = get_kafka_producer()
    log_event = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr,
        'event_type': 'alarm_updated',
        'user_ID': user.id,
        'user_agent': request.headers.get('User-Agent', ''),
        'alarm_id': alarm.id,
        'alarm_name': alarm.name,
        'updated_fields': updated_fields
    }
    producer.produce('logs', key=str(user.id), value=json.dumps(log_event))
    producer.flush()

    return jsonify({
        'status': 'success',
        'message': 'Alarm updated successfully',
        'updated_fields': updated_fields,
        'alarm': alarm.to_dict()
    })

@alarms_bp.route('/<int:alarm_id>/status', methods=['PUT'])
@token_required
def update_alarm_status(alarm_id):
    """Enable or disable an alarm"""
    user = g.user
    data = request.json

    if 'is_active' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing is_active field'
        }), 400

    alarm = Alarm.query.get_or_404(alarm_id)

    # Check if user has permission to update this alarm
    if not user.has_role('admin') and alarm.user_id != user.id:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to update this alarm'
        }), 403

    # Only update if status is actually changing
    if alarm.is_active != data['is_active']:
        old_status = alarm.is_active
        alarm.is_active = data['is_active']
        db.session.commit()

        # Log the status change
        new_status = "enabled" if alarm.is_active else "disabled"
        producer = get_kafka_producer()
        log_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'event_type': 'alarm_status_changed',
            'user_ID': user.id,
            'user_agent': request.headers.get('User-Agent', ''),
            'alarm_id': alarm.id,
            'alarm_name': alarm.name,
            'old_status': old_status,
            'new_status': alarm.is_active
        }
        producer.produce('logs', key=str(user.id), value=json.dumps(log_event))
        producer.flush()

        return jsonify({
            'status': 'success',
            'message': f'Alarm {new_status} successfully',
            'alarm': alarm.to_dict()
        })
    else:
        # No change needed
        status_str = "enabled" if alarm.is_active else "disabled"
        return jsonify({
            'status': 'success',
            'message': f'Alarm already {status_str}',
            'alarm': alarm.to_dict()
        })

@alarms_bp.route('/<int:alarm_id>', methods=['DELETE'])
@token_required
def delete_alarm(alarm_id):
    """Delete an alarm"""
    user = g.user

    alarm = Alarm.query.get_or_404(alarm_id)

    # Check if user has permission to delete this alarm
    if not user.has_role('admin') and alarm.user_id != user.id:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to delete this alarm'
        }), 403

    # Store alarm details for logging before deletion
    alarm_details = {
        'id': alarm.id,
        'name': alarm.name,
        'event_type': alarm.event_type
    }

    db.session.delete(alarm)
    db.session.commit()

    # Log the alarm deletion
    producer = get_kafka_producer()
    log_event = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip_address': request.remote_addr,
        'event_type': 'alarm_deleted',
        'user_ID': user.id,
        'user_agent': request.headers.get('User-Agent', ''),
        'alarm_details': alarm_details
    }
    producer.produce('logs', key=str(user.id), value=json.dumps(log_event))
    producer.flush()

    return jsonify({
        'status': 'success',
        'message': 'Alarm deleted successfully',
        'alarm_details': alarm_details
    })
