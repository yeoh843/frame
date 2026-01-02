#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export PYTHONPATH=$(pwd)
celery -A app.tasks.video_generation worker --loglevel=info --pool=solo










