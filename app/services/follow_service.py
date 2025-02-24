from app.schemas import FollowRequest, User
from sqlalchemy.orm import Session
from app.models import Follower
from app.services.user_service import UserService

user_service = UserService()

class FollowService:
    @staticmethod
    def follow(follow_request: FollowRequest, db: Session, current_user: User):
        user_to_follow = user_service.get_user_by_id(db, follow_request.user_id)

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