# Troubleshooting Guide

## Video Generation Stuck in PENDING

### Problem
After clicking "Generate Video", the job stays in PENDING status and never processes.

### Root Cause
The **Celery worker** is not running or not processing tasks. Celery is responsible for processing video generation jobs in the background.

### Solution

**1. Check if Celery worker is running:**
```powershell
Get-Process python | Where-Object {(Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*celery*"}
```

**2. Start Celery worker:**
```powershell
cd backend
.\start_celery_worker.bat
```

**3. Required Services:**
- ✅ Docker containers running (PostgreSQL, Redis, RabbitMQ)
- ✅ Backend API running (http://localhost:8000)
- ✅ **Celery worker running** (this is usually missing!)

### Quick Start All Services

Use the helper script:
```powershell
cd backend
.\start_all_services.bat
```

This starts both backend and Celery worker in separate windows.

### Verify Everything is Running

1. **Backend**: http://localhost:8000/health should return `{"status":"healthy"}`
2. **Celery**: Check for Python process with "celery" in command line
3. **Redis**: `docker ps` should show `frame-redis-1` running
4. **PostgreSQL**: `docker ps` should show `frame-postgres-1` running

### Common Issues

1. **Multiple Celery workers**: Kill all and start just one
2. **Redis not accessible**: Restart Docker containers
3. **Backend not running**: Start with `start_backend.bat`





