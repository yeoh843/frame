@echo off
cd /d %~dp0
call venv\Scripts\activate
set PYTHONPATH=%CD%

:restart
echo Starting backend server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo Backend stopped. Restarting in 3 seconds...
timeout /t 3 /nobreak >nul
goto restart





