# Project Structure

```
FRAME/
├── ARCHITECTURE.md          # System architecture documentation
├── README.md                 # Project overview
├── SETUP.md                  # Setup instructions
├── DEPLOYMENT.md             # Deployment guide
├── API_EXAMPLES.md           # API usage examples
├── docker-compose.yml        # Local development services
├── .gitignore               # Git ignore rules
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application entry point
│   │   │
│   │   ├── api/             # API routes
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py      # Authentication endpoints
│   │   │   │   ├── videos.py    # Video generation endpoints
│   │   │   │   └── users.py     # User management endpoints
│   │   │
│   │   ├── core/            # Core configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py       # Settings and environment variables
│   │   │
│   │   ├── db/              # Database
│   │   │   ├── __init__.py
│   │   │   ├── database.py     # Database connection
│   │   │   └── models.py       # SQLAlchemy models
│   │   │
│   │   ├── services/        # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── ai_storyboard.py      # GPT-4 storyboard generation
│   │   │   ├── image_enhancement.py  # Nanobanana image enhancement
│   │   │   ├── runway_video.py       # Runway Gen-3 video generation
│   │   │   ├── elevenlabs_voice.py   # ElevenLabs voiceover
│   │   │   ├── video_processor.py    # FFmpeg video processing
│   │   │   ├── music_selector.py     # Music selection
│   │   │   ├── storage.py            # S3 storage service
│   │   │   └── social_media.py       # Social media publishing
│   │   │
│   │   └── tasks/           # Celery tasks
│   │       ├── __init__.py
│   │       └── video_generation.py   # Main video generation workflow
│   │
│   ├── alembic/             # Database migrations
│   │   ├── env.py
│   │   ├── versions/
│   │   └── script.py.mako
│   │
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Docker image for backend
│   ├── alembic.ini          # Alembic configuration
│   └── .env.example         # Environment variables template
│
├── frontend/                # Next.js frontend
│   ├── app/                 # Next.js app directory
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   ├── login/           # Login page
│   │   └── globals.css      # Global styles
│   │
│   ├── components/          # React components
│   │   ├── VideoUpload.tsx  # Image upload component
│   │   └── VideoList.tsx    # Video job list component
│   │
│   ├── lib/                 # Utilities
│   │   └── api.ts           # API client
│   │
│   ├── store/               # State management
│   │   └── authStore.ts     # Authentication store (Zustand)
│   │
│   ├── package.json         # Node dependencies
│   ├── next.config.js       # Next.js configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── tsconfig.json        # TypeScript configuration
│   └── .env.example         # Environment variables template
│
└── workers/                 # (Optional) Separate worker deployment
    └── Dockerfile           # Worker-specific Dockerfile
```

## Key Components

### Backend Services

1. **AI Storyboard Service** (`ai_storyboard.py`)
   - Uses GPT-4 to generate video storyboard
   - Creates shot instructions, subtitles, hooks, CTAs

2. **Image Enhancement Service** (`image_enhancement.py`)
   - Integrates with Nanobanana AI
   - Enhances product images before video generation

3. **Runway Video Service** (`runway_video.py`)
   - Generates videos using Runway Gen-3
   - Handles async video generation with polling

4. **ElevenLabs Voice Service** (`elevenlabs_voice.py`)
   - Generates voiceover from text
   - Supports multiple voices and languages

5. **Video Processor** (`video_processor.py`)
   - FFmpeg-based video processing
   - Combines clips, adds subtitles, mixes audio
   - Resizes for different aspect ratios

6. **Storage Service** (`storage.py`)
   - S3 integration for file storage
   - Handles uploads, downloads, deletions

### Frontend Components

1. **VideoUpload** - Drag & drop image upload
2. **VideoList** - Display and manage video jobs
3. **Auth Store** - Authentication state management

### Task Queue

- **Celery** for async video processing
- **Redis** as message broker
- **RabbitMQ** (optional) for advanced queue management

## Data Flow

1. User uploads images → API stores in S3
2. API creates job → Queues Celery task
3. Worker processes:
   - Enhances images
   - Generates storyboard
   - Creates videos with Runway
   - Generates voiceover
   - Processes and combines videos
   - Uploads final videos to S3
4. User polls for status → Downloads videos

## Extension Points

- Add new AI services in `services/`
- Add new API endpoints in `api/v1/`
- Add new frontend pages in `app/`
- Add new Celery tasks in `tasks/`













