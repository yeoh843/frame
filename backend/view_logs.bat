@echo off
echo ========================================
echo View Logs
echo ========================================
echo.
echo The logs are displayed in the PowerShell windows where services are running.
echo.
echo To view logs in real-time:
echo 1. Check the "Celery Worker" PowerShell window for worker logs
echo 2. Check the "Backend Server" PowerShell window for API logs
echo.
echo Recent log entries (if log files exist):
echo.

if exist celery_worker.log (
    echo === Celery Worker Log (last 50 lines) ===
    powershell -Command "Get-Content celery_worker.log -Tail 50"
    echo.
)

if exist backend.log (
    echo === Backend Server Log (last 50 lines) ===
    powershell -Command "Get-Content backend.log -Tail 50"
    echo.
)

echo.
echo ========================================
echo Tip: To save logs to files, use:
echo   - start_celery_worker_with_logs.bat
echo ========================================
pause


