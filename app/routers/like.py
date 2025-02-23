from fastapi import status, Depends, APIRouter
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas import Like, User
from app.oauth2 import get_current_user
from app.controllers.like_controller import LikeController

router = APIRouter(prefix="/app/like", tags=["Like"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def like(
    like: Like,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return LikeController.like(like, db, current_user)
