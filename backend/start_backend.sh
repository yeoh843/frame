#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export PYTHONPATH=$(pwd)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000










