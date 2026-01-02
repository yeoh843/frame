@echo off
cd /d %~dp0
call venv\Scripts\activate
set PYTHONPATH=%CD%
celery -A app.tasks.video_generation worker --loglevel=info --pool=solo -n worker1@%COMPUTERNAME%





