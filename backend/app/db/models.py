from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.database import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AspectRatio(str, enum.Enum):
    PORTRAIT = "9:16"
    SQUARE = "1:1"
    LANDSCAPE = "16:9"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    subscription_tier = Column(String, default="free")
    credits = Column(Integer, default=10)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    jobs = relationship("Job", back_populates="user")


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Integer, default=0)
    
    # Input
    image_urls = Column(JSON, nullable=False)  # List of S3 URLs
    aspect_ratios = Column(JSON, default=["9:16", "1:1", "16:9"])
    options = Column(JSON, default={})  # User preferences
    
    # Output
    video_urls = Column(JSON)  # Dict: {"9:16": "url", "1:1": "url", ...}
    thumbnail_url = Column(String)
    
    # Metadata
    job_metadata = Column("metadata", JSON, default={})  # Storyboard, subtitles, etc.
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="jobs")


