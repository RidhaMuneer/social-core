from fastapi import status, Depends, APIRouter
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import Like
from app.oauth2 import get_current_user
from app.controllers.like_controller import like_controller

router = APIRouter(prefix="/app/like", tags=["Like"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def like(
    like: Like,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return like_controller(like, db, current_user)
