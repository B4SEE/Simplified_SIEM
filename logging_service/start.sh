#!/bin/bash
#echo "==== install requirements ===="
#pip install -r requirements.txt
echo "==== Starting services from start.sh ===="

# Start Celery worker in the background
celery -A app.celery worker --loglevel=info &
echo "Celery started with PID $!"

# Start Flask app
python run.py --no-reload