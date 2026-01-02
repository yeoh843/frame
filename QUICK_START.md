# Quick Start - See Your Project Running

Follow these steps to get the application running locally.

## Step 1: Install Prerequisites

### Windows
1. **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/)
2. **Node.js 18+**: Download from [nodejs.org](https://nodejs.org/)
3. **Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop/)
4. **FFmpeg**: 
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Or use: `choco install ffmpeg` (if you have Chocolatey)

### Verify Installations
```powershell
python --version    # Should be 3.10+
node --version      # Should be 18+
docker --version
ffmpeg -version
```

## Step 2: Start Database Services

Open PowerShell/Terminal in the project root and run:

```powershell
docker-compose up -d
```

This starts:
- PostgreSQL (database) on port 5432
- Redis (cache/queue) on port 6379
- RabbitMQ (message queue) on port 5672

Verify they're running:
```powershell
docker ps
```

## Step 3: Setup Backend

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
copy .env.example .env

# Edit .env file - add minimum required values:
# DATABASE_URL=postgresql://videogen:videogen_password@localhost:5432/videogen_db
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=your-secret-key-here-change-this
# OPENAI_API_KEY=your-openai-key (optional for testing)
# RUNWAY_API_KEY=your-runway-key (optional for testing)
# ELEVENLABS_API_KEY=your-elevenlabs-key (optional for testing)

# Run database migrations
alembic upgrade head
```

**Note**: For initial testing, you can use placeholder API keys. The app will work but video generation will fail without real keys.

## Step 4: Start Backend Server

Keep the virtual environment activated, then:

```powershell
# In backend directory
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open!**

## Step 5: Start Celery Worker (New Terminal)

Open a **new** PowerShell/Terminal window:

```powershell
cd backend
venv\Scripts\activate
celery -A app.tasks.video_generation.celery_app worker --loglevel=info
```

You should see:
```
celery@hostname ready.
```

**Keep this terminal open!**

## Step 6: Setup Frontend

Open a **third** PowerShell/Terminal window:

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local file
copy .env.example .env.local

# Edit .env.local - should contain:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 7: Start Frontend

```powershell
# In frontend directory
npm run dev
```

You should see:
```
✓ Ready in 2.5s
○ Local:        http://localhost:3000
```

## Step 8: Access the Application

Open your browser and go to:

**Frontend (Main App)**: http://localhost:3000

**Backend API Docs**: http://localhost:8000/api/docs

**Health Check**: http://localhost:8000/health

## Step 9: Test the Application

1. **Register/Login**:
   - Go to http://localhost:3000
   - Click "Login" or navigate to `/login`
   - Create an account or login

2. **Upload Images**:
   - Drag & drop product images (JPG/PNG)
   - Select aspect ratios (9:16, 1:1, 16:9)
   - Click "Generate Video"

3. **View Progress**:
   - Watch the job status update in real-time
   - Progress bar shows processing status

4. **View Results**:
   - Once completed, videos will appear
   - Click to preview and download

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify database is running: `docker ps`
- Check `.env` file exists and has correct values

### Frontend won't start
- Check if port 3000 is already in use
- Verify `npm install` completed successfully
- Check `.env.local` file exists

### Database connection error
```powershell
# Check if PostgreSQL container is running
docker ps

# Restart containers
docker-compose restart
```

### Celery worker not processing
- Verify Redis is running: `docker ps`
- Check REDIS_URL in `.env`
- Look for error messages in worker terminal

### API keys missing
The app will run but video generation will fail. You need:
- OpenAI API key (for storyboard)
- Runway API key (for video generation)
- ElevenLabs API key (for voiceover)
- AWS credentials (for S3 storage)

For testing without real keys, you can modify the services to return mock data.

## Quick Test Without API Keys

If you want to test the UI without real API keys, you can temporarily modify the services to return mock responses. The frontend will work and show the interface, but actual video generation requires real API keys.

## What You Should See

1. **Homepage**: Upload interface with drag & drop
2. **Job List**: Shows all your video generation jobs
3. **Progress**: Real-time progress updates
4. **Videos**: Generated videos in multiple aspect ratios
5. **API Docs**: Interactive API documentation at `/api/docs`

## Next Steps

- Add your real API keys to enable full functionality
- Customize video styles and options
- Set up S3 bucket for video storage
- Configure production deployment

---

**All services running?** You should have 3 terminals open:
1. Backend server (uvicorn)
2. Celery worker
3. Frontend (npm run dev)

Plus Docker containers running in the background!













