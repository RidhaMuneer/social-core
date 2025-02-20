from app.schemas import Like
from sqlalchemy.orm import Session
from app.models import User, Post, Like as LikeModel

def like_service(like: Like, db: Session, current_user: User):
    post = db.query(Post).filter(Post.id == like.post_id).first()

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
        db.commit()
        return True
    else:
        if not found_like:
            False
        like_query.delete(synchronize_session=False)
        db.commit()
        return True
