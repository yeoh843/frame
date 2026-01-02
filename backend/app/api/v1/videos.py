from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from app.db.database import get_db
from app.db.models import User, Job, JobStatus
from app.api.v1.auth import get_current_user
from app.services.storage import StorageService
from app.services.video_processor import VideoProcessor
from app.tasks.video_generation import process_video_job
from pydantic import BaseModel, Field, model_validator

router = APIRouter()


class VideoJobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    image_urls: Optional[List[str]] = None
    video_urls: Optional[dict] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    job_metadata: Optional[dict] = None  # Include metadata for intermediate results
    created_at: str
    
    @model_validator(mode='before')
    @classmethod
    def convert_job(cls, data):
        if hasattr(data, 'id'):
            # Convert SQLAlchemy Job model to dict
            return {
                'job_id': str(data.id),
                'status': data.status.value if hasattr(data.status, 'value') else str(data.status),
                'progress': data.progress,
                'image_urls': data.image_urls,
                'video_urls': data.video_urls,
                'thumbnail_url': data.thumbnail_url,
                'error_message': getattr(data, 'error_message', None),
                'job_metadata': getattr(data, 'job_metadata', None),
                'created_at': data.created_at.isoformat() if hasattr(data.created_at, 'isoformat') else str(data.created_at),
            }
        return data
    
    class Config:
        from_attributes = True


class VideoCreateRequest(BaseModel):
    aspect_ratios: List[str] = ["9:16", "1:1", "16:9"]
    options: dict = {}


@router.post("/", response_model=VideoJobResponse)
async def create_video_job(
    images: List[UploadFile] = File(...),
    aspect_ratios: str = Form("9:16"),  # Use Form() for form data fields, default to single ratio
    video_provider: str = Form("seedream"),  # Video service provider selection
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new video generation job"""
    
    # Check user credits
    if current_user.credits < 1:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Validate images
    if len(images) < 1:
        raise HTTPException(status_code=400, detail="At least one image is required")
    
    if len(images) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
    
    # Upload images to S3
    storage = StorageService()
    image_urls = []
    
    for image in images:
        # Validate file type
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Invalid file type: {image.content_type}")
        
        url = await storage.upload_file(image.file, f"uploads/{current_user.id}/{image.filename}")
        image_urls.append(url)
    
    # Parse aspect ratios
    aspect_ratio_list = [ar.strip() for ar in aspect_ratios.split(",")]
    
    # Validate video provider
    valid_providers = ["seedream", "openai", "kling", "veo3"]
    if video_provider not in valid_providers:
        video_provider = "seedream"  # Default to seedream if invalid
    
    # Create job
    job = Job(
        user_id=current_user.id,
        status=JobStatus.PENDING,
        image_urls=image_urls,
        aspect_ratios=aspect_ratio_list,
        options={"video_provider": video_provider}  # Store provider in options
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Deduct credit
    current_user.credits -= 1
    db.commit()
    
    # Queue job for processing
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Queueing video generation job {job.id} with {len(image_urls)} images")
    try:
        result = process_video_job.delay(str(job.id))
        logger.info(f"Job {job.id} queued successfully, Celery task ID: {result.id}")
    except Exception as e:
        logger.error(f"Failed to queue job {job.id}: {str(e)}", exc_info=True)
        # If queueing fails, mark job as failed
        job.status = JobStatus.FAILED
        job.error_message = f"Failed to queue job: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to queue video generation job: {str(e)}")
    
    return job


@router.get("/{job_id}", response_model=VideoJobResponse)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get video generation job status"""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/", response_model=List[VideoJobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's video generation jobs (newest first)"""
    jobs = db.query(Job).filter(Job.user_id == current_user.id).order_by(desc(Job.created_at)).offset(skip).limit(limit).all()
    return jobs


@router.delete("/{job_id}")
async def delete_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a video generation job"""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files from storage
    storage = StorageService()
    if job.video_urls:
        for url in job.video_urls.values():
            await storage.delete_file(url)
    
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}




