from flask import Blueprint, request, jsonify
from ..log_ingester import produce_log

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.route('/logs', methods=['POST'])
def receive_logs():
    log_data = request.json
    produce_log(log_data)
    return jsonify({"message": "Log received"}), 200