# API Usage Examples

## Authentication

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepassword123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Video Generation

### Create Video Job
```bash
curl -X POST http://localhost:8000/api/v1/videos/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "images=@product1.jpg" \
  -F "images=@product2.jpg" \
  -F "aspect_ratios=9:16,1:1,16:9"
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0,
  "video_urls": null,
  "thumbnail_url": null,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Get Job Status
```bash
curl -X GET http://localhost:8000/api/v1/videos/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "video_urls": null,
  "thumbnail_url": "https://s3.amazonaws.com/bucket/thumbnails/...",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### List All Jobs
```bash
curl -X GET http://localhost:8000/api/v1/videos/?skip=0&limit=20 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Delete Job
```bash
curl -X DELETE http://localhost:8000/api/v1/videos/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Python SDK Example

```python
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "your_access_token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Create video job
files = [
    ("images", open("product1.jpg", "rb")),
    ("images", open("product2.jpg", "rb"))
]
data = {"aspect_ratios": "9:16,1:1,16:9"}

response = requests.post(
    f"{BASE_URL}/api/v1/videos/",
    headers=headers,
    files=files,
    data=data
)
job = response.json()
job_id = job["job_id"]

# Poll for completion
import time
while True:
    response = requests.get(
        f"{BASE_URL}/api/v1/videos/{job_id}",
        headers=headers
    )
    job = response.json()
    
    if job["status"] == "completed":
        print("Video ready!")
        print(f"Videos: {job['video_urls']}")
        break
    elif job["status"] == "failed":
        print(f"Failed: {job.get('error_message')}")
        break
    
    print(f"Progress: {job['progress']}%")
    time.sleep(5)
```

## JavaScript/TypeScript Example

```typescript
const API_URL = 'http://localhost:8000';
const token = 'your_access_token';

// Create video job
const formData = new FormData();
formData.append('images', file1);
formData.append('images', file2);
formData.append('aspect_ratios', '9:16,1:1,16:9');

const response = await fetch(`${API_URL}/api/v1/videos/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const job = await response.json();

// Poll for status
const pollJob = async (jobId: string) => {
  const checkStatus = async () => {
    const res = await fetch(`${API_URL}/api/v1/videos/${jobId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const job = await res.json();
    
    if (job.status === 'completed') {
      console.log('Video ready!', job.video_urls);
      return job;
    } else if (job.status === 'failed') {
      throw new Error(job.error_message);
    }
    
    console.log(`Progress: ${job.progress}%`);
    setTimeout(checkStatus, 5000);
  };
  
  await checkStatus();
};

await pollJob(job.job_id);
```

## Webhook Example

Configure webhook URL when creating job (future feature):

```json
{
  "images": [...],
  "aspect_ratios": ["9:16", "1:1", "16:9"],
  "webhook_url": "https://your-domain.com/webhook"
}
```

Webhook payload:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "video_urls": {
    "9:16": "https://s3.amazonaws.com/...",
    "1:1": "https://s3.amazonaws.com/...",
    "16:9": "https://s3.amazonaws.com/..."
  }
}
```













