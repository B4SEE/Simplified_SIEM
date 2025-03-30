import sys

from flask import Blueprint, request, jsonify
from ..log_ingester import produce_log
from ..log_processor import consume_log

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route('/logs', methods=['POST'])
def receive_logs():
    print('command: receive_logs', file=sys.stderr)
    log_data = request.json
    outcome = produce_log(log_data)
    if outcome:
        return jsonify({"message": "Log received"}), 200
    return jsonify({"message": "Log received but not saved"}), 505

@api_bp.route('/process_logs', methods=['POST'])
def process_logs_endpoint():
    consume_log()
    return jsonify({"message": "Logs processed"}), 200
