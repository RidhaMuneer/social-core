from app.schemas import FollowRequest, User
from sqlalchemy.orm import Session
from app.services.follow_service import FollowService
from fastapi import HTTPException, status, Response

class FollowController:
    @staticmethod
    def follow(follow_request: FollowRequest, db: Session, current_user: User):
        follow = FollowService.follow(follow_request, db, current_user)

        if follow is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
    
        if follow is False:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
            )
    
        return Response(status_code=status.HTTP_200_OK)
