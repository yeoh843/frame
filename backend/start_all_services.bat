@echo off
echo Starting all services for video generation...
echo.

echo [1/3] Starting Backend API...
start "Backend API" cmd /k "cd /d %~dp0 && call venv\Scripts\activate && set PYTHONPATH=%CD% && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Celery Worker...
start "Celery Worker" cmd /k "cd /d %~dp0 && call venv\Scripts\activate && set PYTHONPATH=%CD% && celery -A app.tasks.video_generation worker --loglevel=info --pool=solo"

timeout /t 2 /nobreak >nul

echo [3/3] Checking services...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Services started! Keep these windows open.
echo Press any key to exit this window (services will keep running)...
pause >nul





