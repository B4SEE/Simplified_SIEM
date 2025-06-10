import sys
import logging

from .celery import celery_app
from .log_processor import LogProcessorSingleton

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def analyze_logs(self):
    """Process logs from Kafka and store them in Elasticsearch and PostgreSQL."""
    try:
        log_processor = LogProcessorSingleton()
        if not log_processor:
            logger.error("Log Processor Singleton initialization failed")
            raise Exception("Log Processor Singleton initialization failed")

        # Try to consume and process logs
        success = log_processor.consume_log()
        
        if success:
            logger.info("Successfully processed log messages")
        else:
            logger.warning("No messages processed in this batch")
            
        return success
    except Exception as e:
        logger.error(f"Error in analyze_logs task: {e}")
        # Retry the task with exponential backoff
        retry_in = (self.request.retries + 1) * 60  # 60s, 120s, 180s
        raise self.retry(exc=e, countdown=retry_in)
