from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

celery_app = Celery(
    "logging_service",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
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

celery_app.conf.beat_schedule = {
    'analyze-logs-every-5-seconds': {
        'task': 'app.celery_tasks.analyze_logs',
        'schedule': timedelta(seconds=5),
    },
}

celery_app.conf.timezone = 'UTC'
from app.celery_tasks import analyze_logs