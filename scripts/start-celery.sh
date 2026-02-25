#!/bin/bash
# Start Celery Worker

set -e

echo "================================"
echo "Starting Celery Worker"
echo "================================"

# Set environment variables
export USE_CELERY=true

# Activate virtual environment (if exists)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

cd backend

# Start Celery Worker
celery -A celery_app worker --loglevel=info --concurrency=4
