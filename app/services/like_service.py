from app.schemas import Like
from sqlalchemy.orm import Session
from app.models import User, Like as LikeModel
from app.services.post_service import PostService

post_service = PostService()

class LikeService:
    @staticmethod
    def like(like: Like, db: Session, current_user: User):
        post = post_service.get_by_id(db, like.post_id)

        if not post:
            return None

        like_query = db.query(LikeModel).filter(
            LikeModel.post_id == like.post_id, LikeModel.user_id == current_user.id
        )
        found_like = like_query.first()

        if like.dir == 1:
            if found_like:
                return False
        
            new_like = LikeModel(post_id=like.post_id, user_id=current_user.id)
            db.add(new_like)
            post.likes += 1 
            db.commit()
            return True
        else: 
            if not found_like:
                return False
            like_query.delete(synchronize_session=False)
            post.likes = max(0, post.likes - 1)
            db.commit()
            return True
