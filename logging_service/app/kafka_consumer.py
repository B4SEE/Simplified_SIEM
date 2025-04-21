# logging_service/app/kafka_consumer.py
import sys
import time
from threading import Thread
from .log_processor import LogProcessorSingleton


def consume_logs_in_background():
    log_processor = LogProcessorSingleton()
    if not log_processor:
        print("Log Processor Singleton initialization failed, kafka consumer thread will not be running", file=sys.stderr)
        return
    while True:
        try:
            log_processor.consume_log()
            time.sleep(1)
        except Exception as e:
            print(f"Error while consuming log: {e}", file=sys.stderr)
            time.sleep(5)


def start_kafka_consumer_thread():
    thread = Thread(target=consume_logs_in_background)
    thread.daemon = True
    thread.start()