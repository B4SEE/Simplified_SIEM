from flask import Blueprint, request, jsonify
from ..log_ingester import produce_log

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route('/logs', methods=['POST'])
def receive_logs():
    log_data = request.json
    print(log_data)
    outcome = produce_log(log_data)
    if outcome:
        return jsonify({"message": "Log received"}), 200
    return jsonify({"message": "Log received but not saved"}), 505

