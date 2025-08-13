#!/bin/bash
touch /home/site/wwwroot/started.txt
source /home/site/wwwroot/venv/bin/activate
python manage.py migrate
gunicorn --bind=0.0.0.0:8000 student_alerts_app.wsgi:application


