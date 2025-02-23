from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from app.models import Post, User, Like
from typing import Optional
from app.schemas import PostCreate

class PostService:
    @staticmethod
    def get_post_by_id(post_id: int, user_id: int, db: Session):
        return (
            db.query(
                Post,
                User.id,
                User.username,
                User.image_url,
                exists().where((Like.post_id == Post.id) & (Like.user_id == user_id)).label("isLiked")
            )
            .join(User, User.id == Post.owner_id)
            .filter(Post.id == post_id, Post.published)
            .first()
        )

    @staticmethod
    def get_all_posts(db: Session, limit: int = 10, search: Optional[str] = "", current_user: User = None):    
        return (
            db.query(
                Post,
                User.id,
                User.username,
                User.image_url,
                exists().where((Like.post_id == Post.id) & (Like.user_id == current_user.id)).label("isLiked")
            )
            .join(User, User.id == Post.owner_id)
            .group_by(Post.id, User.id)
            .filter(Post.content.contains(search), Post.published)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_post(content: str, published: bool, db: Session, image_url: str, current_user: User):
        new_post = Post(
            owner_id=current_user.id,
            image_url=image_url,
            content=content,
            published=published,
            likes=0,
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)

    @staticmethod
    def delete_post(post_id: int, db: Session, current_user: User):
        post_query = db.query(Post).filter(Post.id == post_id)
        post = post_query.first()

        if not post:
            return None 
        if post.owner_id != current_user.id:
            return False 

        post_query.delete(synchronize_session=False)
        db.commit()
        return True 

    @staticmethod
    def update_post(post_data: PostCreate, db: Session, current_user: User, post_id: int):
        post_query = db.query(Post).filter(Post.id == post_id)
        post = post_query.first()

        if not post:
            return None 
        if post.owner_id != current_user.id:
            return False 

        post_query.update(post_data.dict(), synchronize_session=False)
        db.commit()
        return True