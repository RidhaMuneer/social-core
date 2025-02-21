from app.schemas import FollowRequest, User
from sqlalchemy.orm import Session
from app.models import User as UserModel, Follower

def follow_service(follow_request: FollowRequest, db: Session, current_user: User):
    user_to_follow = (
        db.query(UserModel).filter(UserModel.id == follow_request.user_id).first()
    )
    if not user_to_follow:
        return None
    
    follow_query = db.query(Follower).filter(
        Follower.following_id == follow_request.user_id,
        Follower.follower_id == current_user.id,
    )
    found_follow = follow_query.first()

    if follow_request.dir == 1:
        if found_follow:
            return False
        new_follow = Follower(
            following_id=follow_request.user_id, follower_id=current_user.id
        )
        db.add(new_follow)
        db.commit()
        return True
    else:
        if not found_follow:
            return False
        follow_query.delete(synchronize_session=False)
        db.commit()
        return True