@echo off
cd /d %~dp0
call venv\Scripts\activate
set PYTHONPATH=%CD%
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


