# How to Restart Backend and Celery Worker

## Quick Guide

### 1. Start Backend API (with --reload for auto-reload)

**Windows:**
```powershell
cd backend
.\start_backend.bat
```

**Or manually:**
```powershell
cd backend
.\venv\Scripts\activate
set PYTHONPATH=%CD%
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**What `--reload` does:**
- Automatically restarts backend when you change Python code
- You DON'T need to manually restart if using `--reload`
- Just save your code changes and the backend auto-restarts

**To stop backend:**
- Press `Ctrl+C` in the terminal

---

### 2. Start Celery Worker

**Windows:**
```powershell
cd backend
.\start_celery_worker.bat
```

**Or manually:**
```powershell
cd backend
.\venv\Scripts\activate
set PYTHONPATH=%CD%
celery -A app.tasks.video_generation worker --loglevel=info --pool=solo
```

**To stop Celery worker:**
- Press `Ctrl+C` in the terminal

**IMPORTANT:** 
- Celery worker does NOT auto-reload
- If you change code in `app/tasks/` or `app/services/`, you MUST restart Celery worker
- Stop with `Ctrl+C`, then run the start command again

---

## Restart Process

### Scenario 1: You Changed Backend Code (API, routes, etc.)

**If backend was started with `--reload`:**
- ✅ No restart needed - it auto-reloads
- Just save your file and wait 1-2 seconds

**If backend was started WITHOUT `--reload`:**
1. Go to backend terminal
2. Press `Ctrl+C` to stop
3. Run `.\start_backend.bat` again

### Scenario 2: You Changed Celery Worker Code (tasks, video generation)

1. Go to Celery worker terminal
2. Press `Ctrl+C` to stop
3. Run `.\start_celery_worker.bat` again

### Scenario 3: You Changed Both

1. Restart backend (if not using --reload)
2. Restart Celery worker

---

## Check if Services are Running

### Backend API:
- Open browser: http://localhost:8000/health
- Should see: `{"status":"healthy"}`

### Celery Worker:
- Check terminal window - should see "celery@hostname ready."
- If terminal is closed, worker is NOT running

---

## Troubleshooting

**Backend won't start:**
- Check if port 8000 is in use
- Make sure virtual environment is activated
- Check if database is running (docker-compose up -d)

**Celery worker won't start:**
- Check if Redis is running (docker-compose up -d)
- Make sure virtual environment is activated
- Check REDIS_URL in .env file

**Changes not taking effect:**
- Backend: Make sure you're using `--reload` flag
- Celery: Must manually restart after code changes










