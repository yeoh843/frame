@echo off
cd /d %~dp0
call venv\Scripts\activate
set PYTHONPATH=%CD%

echo Starting Celery worker with logs saved to celery_worker.log...
celery -A app.tasks.video_generation worker --loglevel=info --pool=solo -n worker@%COMPUTERNAME% > celery_worker.log 2>&1


