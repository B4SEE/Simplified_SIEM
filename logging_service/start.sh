#!/bin/bash
echo "==== Starting services from start.sh ===="

celery -A app.celery.celery_app worker --beat --loglevel=info &

CELERY_PID=$!
echo "Celery started with PID $CELERY_PID"

exec python run.py