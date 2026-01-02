from fastapi import APIRouter
from app.api.v1 import auth, videos, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(users.router, prefix="/users", tags=["users"])













