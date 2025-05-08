import sys

from .celery import celery_app
import logging

from .log_processor import LogProcessorSingleton


@celery_app.task
def analyze_logs():
    log_processor = LogProcessorSingleton()
    if not log_processor:
        logging.info("Log Processor Singleton initialization failed, kafka consumer thread will not be running")
        return

    try:
        log_processor.consume_log()
    except Exception as e:
        logging.info("Log consuming failed: " + e)
