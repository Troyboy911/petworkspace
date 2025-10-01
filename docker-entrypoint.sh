#!/bin/bash

# Start Xvfb for headless Chrome
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99

# Wait for Xvfb to start
sleep 2

# Create necessary directories if they don't exist
mkdir -p logs data config/proxies models temp

# Set proper permissions
chmod 755 logs data config/proxies models temp

# Initialize database if needed
echo "Initializing database..."
cd /app
python -c "
from src.models import create_database, create_session
from config.config import Config
import os

# Create database
database_url = Config.DATABASE_URL
if database_url.startswith('sqlite'):
    # For SQLite, ensure directory exists
    db_path = database_url.replace('sqlite:///', '')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_database(Config.DATABASE_URL)
session = create_session(engine)
print('Database initialized successfully')
"

# Start the application based on the command
if [ "$1" = "web" ]; then
    echo "Starting web server..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 src.dashboard.app:app
elif [ "$1" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A src.celery_app worker --loglevel=info --concurrency=4
elif [ "$1" = "scheduler" ]; then
    echo "Starting Celery scheduler..."
    exec celery -A src.celery_app beat --loglevel=info
elif [ "$1" = "scraper" ]; then
    echo "Starting scraper service..."
    exec python -m src.scrapers.main
elif [ "$1" = "social" ]; then
    echo "Starting social media service..."
    exec python -m src.social.main
elif [ "$1" = "affiliate" ]; then
    echo "Starting affiliate service..."
    exec python -m src.affiliate.main
elif [ "$1" = "dropshipping" ]; then
    echo "Starting dropshipping service..."
    exec python -m src.dropshipping.main
elif [ "$1" = "ml" ]; then
    echo "Starting ML service..."
    exec python -m src.ml.main
else
    # Default: run the provided command
    echo "Executing custom command: $@"
    exec "$@"
fi