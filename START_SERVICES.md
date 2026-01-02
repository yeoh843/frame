# How to Start All Services

## Prerequisites Check
✅ Python 3.13 installed
✅ Node.js 22 installed  
⚠️ Docker not installed (you'll need it for database/Redis)

## Setup Complete! ✅

Backend dependencies installed (some may need Rust for full compilation)
Frontend dependencies installed
Environment files created

## Starting Services

### Option 1: Without Docker (Limited - Database needed)

You need PostgreSQL and Redis running. Options:
1. Install PostgreSQL and Redis locally
2. Use Docker Desktop (recommended)
3. Use cloud services (Supabase for PostgreSQL, Upstash for Redis)

### Option 2: With Docker (Recommended)

1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop/

2. **Start database services:**
```powershell
docker-compose up -d
```

3. **Run database migrations:**
```powershell
cd backend
.\venv\Scripts\activate
alembic upgrade head
```

4. **Start Backend API** (Terminal 1):
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

5. **Start Celery Worker** (Terminal 2):
```powershell
cd backend
.\venv\Scripts\activate
celery -A app.tasks.video_generation.celery_app worker --loglevel=info
```

6. **Start Frontend** (Terminal 3):
```powershell
cd frontend
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## Quick Test (Without Database)

You can test the frontend UI even without a database:

1. Start frontend: `cd frontend && npm run dev`
2. Open http://localhost:3000
3. The UI will load but API calls will fail without backend

## Next Steps

1. Install Docker Desktop
2. Start docker-compose services
3. Run migrations
4. Start all three services (backend, worker, frontend)
5. Add your API keys to `backend/.env` for full functionality













