from app.schemas import Like
from app.models import User
from sqlalchemy.orm import Session
from app.services.like_service import like_service
from fastapi import status, HTTPException, Response

def like_controller(like: Like, db: Session, current_user: User):
    like = like_service(like, db, current_user)

    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    
    if like is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user has already liked the post",
        )
    
    return Response(status_code=status.HTTP_200_OK)
