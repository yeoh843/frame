@echo off
cd /d %~dp0
echo ========================================
echo Viewing Celery Worker Logs (Last 100 lines)
echo ========================================
echo.

if exist celery_worker.log (
    powershell -Command "Get-Content celery_worker.log -Tail 100"
) else (
    echo Log file not found. Worker may not be running with logging enabled.
    echo Check the Celery worker PowerShell window for real-time logs.
)

echo.
echo ========================================
echo Press any key to refresh, or Ctrl+C to exit
echo ========================================
pause > nul
goto :eof


