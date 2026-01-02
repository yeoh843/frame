from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.api.v1.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()


class UserResponse(BaseModel):
    id: str
    email: str
    subscription_tier: str
    credits: int
    
    class Config:
        from_attributes = True


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user













