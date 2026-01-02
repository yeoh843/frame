# Setup Guide

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- FFmpeg installed
- PostgreSQL (or use Docker)
- Redis (or use Docker)

## Quick Start

### 1. Clone and Setup

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 2. Configure Environment

#### Backend (.env)
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

Required API Keys:
- OpenAI API key (for storyboard generation)
- Runway API key (for video generation)
- ElevenLabs API key (for voiceover)
- Nanobanana API key (for image enhancement)
- AWS credentials (for S3 storage)

#### Frontend (.env.local)
```bash
cd frontend
cp .env.example .env.local
# Edit .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Services

```bash
# Start PostgreSQL, Redis, RabbitMQ
docker-compose up -d

# Run database migrations
cd backend
alembic upgrade head

# Start backend API
uvicorn app.main:app --reload

# In another terminal, start Celery worker
celery -A app.tasks.video_generation.celery_app worker --loglevel=info

# In another terminal, start frontend
cd frontend
npm run dev
```

### 4. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- RabbitMQ Management: http://localhost:15672 (admin/admin)

## Development Workflow

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Formatting

```bash
# Backend
cd backend
black app/
isort app/

# Frontend
cd frontend
npm run lint
```

## Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment instructions.

## Troubleshooting

### FFmpeg not found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Database connection errors
- Check PostgreSQL is running: `docker ps`
- Verify DATABASE_URL in .env
- Check database exists: `psql -U user -d videogen_db`

### Celery worker not processing
- Check Redis is running
- Verify REDIS_URL in .env
- Check worker logs for errors

### API key errors
- Verify all API keys are set in .env
- Check API key permissions and quotas
- Review API service status pages

## Next Steps

1. Set up monitoring (Sentry, Datadog)
2. Configure CDN for video delivery
3. Set up CI/CD pipeline
4. Add unit and integration tests
5. Configure production database backups
6. Set up logging aggregation













