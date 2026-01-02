# Deployment Guide

## Production Deployment Architecture

### Infrastructure Components

1. **Application Servers**: FastAPI backend (containerized)
2. **Worker Servers**: Celery workers for video processing
3. **Database**: PostgreSQL (managed service recommended)
4. **Cache/Queue**: Redis + RabbitMQ
5. **Storage**: AWS S3 / GCP Cloud Storage
6. **CDN**: Cloudflare / AWS CloudFront
7. **Frontend**: Next.js (Vercel / AWS Amplify)

## Deployment Options

### Option 1: AWS Deployment

#### Backend (ECS/Fargate)
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    ports:
      - "8000:8000"
  
  worker:
    build: ./backend
    command: celery -A app.tasks.video_generation.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
```

#### Infrastructure Setup
- **RDS PostgreSQL**: Managed database
- **ElastiCache Redis**: For caching and Celery broker
- **S3 Bucket**: For video storage
- **ECS Cluster**: For backend and workers
- **Application Load Balancer**: For API routing

### Option 2: GCP Deployment

#### Cloud Run (Serverless)
```bash
# Deploy backend
gcloud run deploy videogen-api \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy workers (Cloud Run Jobs)
gcloud run jobs create videogen-worker \
  --source ./backend \
  --region us-central1
```

#### Infrastructure
- **Cloud SQL**: PostgreSQL
- **Memorystore**: Redis
- **Cloud Storage**: Video files
- **Cloud CDN**: Content delivery

### Option 3: Railway / Render (Simplified)

#### Railway
1. Connect GitHub repository
2. Add services:
   - PostgreSQL
   - Redis
   - Backend service
   - Worker service
3. Configure environment variables
4. Deploy

#### Render
1. Create Web Service for backend
2. Create Background Worker for Celery
3. Add PostgreSQL and Redis services
4. Configure environment variables

## Environment Variables (Production)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis
REDIS_URL=redis://host:6379/0

# JWT
SECRET_KEY=<generate-strong-secret>

# AWS S3
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_REGION=us-east-1
S3_BUCKET_NAME=videogen-prod

# AI APIs
OPENAI_API_KEY=<key>
RUNWAY_API_KEY=<key>
ELEVENLABS_API_KEY=<key>
NANOBANANA_API_KEY=<key>

# Monitoring
SENTRY_DSN=<dsn>
```

## Frontend Deployment

### Vercel (Recommended)
```bash
cd frontend
vercel --prod
```

### AWS Amplify
1. Connect GitHub repository
2. Configure build settings:
   - Build command: `npm run build`
   - Output directory: `.next`
3. Add environment variables
4. Deploy

## Monitoring & Logging

### Sentry Setup
```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Datadog Setup
- Install Datadog agent on servers
- Configure APM for Python
- Set up dashboards for:
  - Job processing times
  - Error rates
  - Queue depth
  - API response times

## Scaling Considerations

### Horizontal Scaling
- **API Servers**: Auto-scale based on CPU/memory
- **Workers**: Scale based on queue depth
  - Target: < 100 jobs in queue
  - Scale up when queue > 50
  - Scale down when queue < 10

### Database Scaling
- Use read replicas for analytics
- Connection pooling (PgBouncer)
- Index optimization

### Storage Optimization
- Enable S3 lifecycle policies
- Archive old videos to Glacier
- Use CDN for video delivery

## Security Checklist

- [ ] Enable HTTPS/TLS everywhere
- [ ] Use strong JWT secret key
- [ ] Enable database encryption at rest
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable S3 bucket encryption
- [ ] Use IAM roles (not access keys)
- [ ] Enable WAF for API
- [ ] Set up DDoS protection
- [ ] Regular security audits

## Backup Strategy

### Database Backups
- Daily automated backups
- 30-day retention
- Cross-region replication

### Video Backups
- S3 versioning enabled
- Lifecycle policy for old versions
- Cross-region replication for critical videos

## Cost Optimization

1. **Use Spot Instances** for workers (non-critical)
2. **Reserved Instances** for baseline load
3. **S3 Intelligent Tiering** for storage
4. **Cache AI responses** to reduce API costs
5. **Compress videos** before storage
6. **Auto-scale down** during low traffic

## CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Build and deploy steps
```

## Health Checks

### API Health Endpoint
```python
@app.get("/health")
async def health():
    # Check database
    # Check Redis
    # Check S3
    return {"status": "healthy"}
```

### Monitoring Endpoints
- `/health`: Basic health check
- `/metrics`: Prometheus metrics
- `/api/docs`: API documentation

## Troubleshooting

### Common Issues

1. **Worker not processing jobs**
   - Check Celery connection to Redis
   - Verify worker logs
   - Check queue depth

2. **Video generation fails**
   - Check Runway API quota
   - Verify S3 permissions
   - Check FFmpeg installation

3. **High costs**
   - Review AI API usage
   - Optimize video processing
   - Enable caching

## Support

For deployment issues, check:
- Application logs
- Worker logs
- Database logs
- Monitoring dashboards













