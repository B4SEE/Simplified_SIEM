from flask import Blueprint, request, jsonify
from ..log_ingester import KafkaProducerSingleton
from ..log_processor import LogProcessorSingleton

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

@api_bp.route('/process_logs', methods=['POST'])
def process_logs_endpoint():
    log_processor = LogProcessorSingleton()
    if not log_processor:
        return jsonify({"error": "Log Processor Singleton not initialized"}), 500
    log_processor.consume_log()
    return jsonify({"message": "Logs processed"}), 200
