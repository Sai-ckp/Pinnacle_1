#!/bin/bash
set -euo pipefail

LOG_FILE="/home/LogFiles/startup.log"
echo "=== Startup initiated at $(date) ===" >> "$LOG_FILE"

cd /home/site/wwwroot || exit 1
echo "Current directory: $(pwd)" >> "$LOG_FILE"

# Use Azure-provided Python environment
export PATH="/antenv/bin:$PATH"
export PYTHONPATH="/antenv/lib/python3.9/site-packages:$PYTHONPATH"

# Django settings
export DJANGO_SETTINGS_MODULE=student_alerts_app.settings
echo "DJANGO_SETTINGS_MODULE set to $DJANGO_SETTINGS_MODULE" >> "$LOG_FILE"

# ✅ Install dependencies
echo "Installing Python packages..." >> "$LOG_FILE"
pip install -r requirements.txt >> "$LOG_FILE" 2>&1 || echo "Pip install failed" >> "$LOG_FILE"

# Run migrations
echo "Running migrations..." >> "$LOG_FILE"
python manage.py migrate --noinput >> "$LOG_FILE" 2>&1 || echo "Migration failed" >> "$LOG_FILE"

# Collect static files
echo "Collecting static files..." >> "$LOG_FILE"
python manage.py collectstatic --noinput >> "$LOG_FILE" 2>&1 || echo "Collectstatic failed" >> "$LOG_FILE"

# Start Gunicorn
PORT=${PORT:-8000}
echo "Starting Gunicorn on port $PORT..." >> "$LOG_FILE"
exec gunicorn student_alerts_app.wsgi:application \
    --bind=0.0.0.0:$PORT \
    --workers=3 \
    --threads=2 \
    --timeout=300 >> "$LOG_FILE" 2>&1
