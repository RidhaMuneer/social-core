from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..oauth2 import get_current_user

router = APIRouter(prefix="/app/follow", tags=["Follow"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def follow(
    follow_request: schemas.FollowRequest,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    user_to_follow = (
        db.query(models.User).filter(models.User.id == follow_request.user_id).first()
    )
    if not user_to_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    follow_query = db.query(models.Follower).filter(
        models.Follower.following_id == follow_request.user_id,
        models.Follower.follower_id == current_user.id,
    )
    found_follow = follow_query.first()

    if follow_request.dir == 1:
        if found_follow:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already following this user",
            )
        new_follow = models.Follower(
            following_id=follow_request.user_id, follower_id=current_user.id
        )
        db.add(new_follow)
        db.commit()
        return {"message": "User followed"}
    else:
        if not found_follow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not following this user",
            )
        follow_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "User unfollowed"}
