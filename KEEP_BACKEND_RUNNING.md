# How to Keep Backend Running

## Problem
The backend server stops when:
- Terminal window is closed
- Process crashes
- System restarts

## Solution 1: Use Persistent Batch Script

Run this instead of `start_backend.bat`:
```powershell
cd backend
.\start_backend_persistent.bat
```

This will auto-restart if the backend crashes.

## Solution 2: Run as Windows Service (Advanced)

You can use NSSM (Non-Sucking Service Manager) to run the backend as a Windows service that starts automatically.

## Solution 3: Use Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "When I log on"
4. Action: Start a program
5. Program: `C:\FRAME\backend\start_backend.bat`
6. Check "Run whether user is logged on or not"

## Quick Check Commands

Check if backend is running:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

Check if port 8000 is in use:
```powershell
netstat -ano | findstr ":8000"
```

## Current Status
- Backend should be running on http://localhost:8000
- If it stops, run `start_backend_persistent.bat` for auto-restart





