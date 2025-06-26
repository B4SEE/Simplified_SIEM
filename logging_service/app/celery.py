from celery import Celery
from celery.schedules import crontab
import os

celery_app = Celery('logging_service',
                    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
                    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'))

# Configure Celery
celery_app.conf.update(
    worker_concurrency=1,  # Use only one worker
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'analyze-logs-every-5-seconds': {
            'task': 'app.celery_tasks.analyze_logs',
            'schedule': 5.0,
        },
    }
)

celery_app.conf.task_routes = {
    'app.celery_tasks.analyze_logs': {'queue': 'logs'}
}

celery_app.conf.task_queues = {
    'logs': {
        'exchange': 'logs',
        'routing_key': 'logs',
    },
}

from app.celery_tasks import analyze_logs