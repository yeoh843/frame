# AI Video Generation SaaS Platform

Automated product video generation platform with AI-powered storyboarding, video creation, and social media publishing.

## Features

- 🎬 Automatic video generation from product images
- 🤖 AI storyboard & copywriting (GPT-4)
- 🎥 Runway Gen-3 video generation
- ✂️ FFmpeg video editing & composition
- 🎤 ElevenLabs voiceover generation
- 📱 Direct publishing to TikTok, Instagram, YouTube
- 🎨 Multiple aspect ratios (9:16, 1:1, 16:9)
- 🎵 Automatic music selection & beat sync

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Queue**: Celery + RabbitMQ
- **Storage**: AWS S3 / GCP Cloud Storage
- **AI Services**: OpenAI GPT-4, Runway Gen-3, ElevenLabs, Nanobanana

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- FFmpeg installed

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your API keys
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Start Services (Docker)

```bash
docker-compose up -d
```

## Project Structure

```
├── backend/           # FastAPI backend
├── frontend/          # Next.js frontend
├── workers/           # Celery workers
├── shared/            # Shared utilities
└── docker-compose.yml # Local development setup
```

## Environment Variables

See `.env.example` files in each directory for required configuration.

## License

MIT













