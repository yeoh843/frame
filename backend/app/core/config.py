from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    
    # OpenAI (for Sora/Video Generation)
    OPENAI_API_KEY: str = ""
    
    # Seedream
    SEEDREAM_API_KEY: str = ""
    
    # Kling AI
    KLING_API_KEY: str = ""
    
    # Veo3 (Google)
    VEO3_API_KEY: str = ""
    
    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    
    # Nanobanana
    NANOBANANA_API_KEY: str = ""
    
    # Social Media
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # API Base URL (for generating URLs in production)
    API_BASE_URL: str = "http://localhost:8000"
    
    # Environment
    ENVIRONMENT: str = "development"  # development, production
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        # Use absolute path to .env file in backend directory
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        case_sensitive = True


settings = Settings()

