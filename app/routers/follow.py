from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FollowRequest, User
from app.oauth2 import get_current_user
from app.controllers.follow_controller import FollowController

router = APIRouter(prefix="/app/follow", tags=["Follow"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def follow(
    follow_request: FollowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return FollowController.follow(follow_request, db, current_user)
