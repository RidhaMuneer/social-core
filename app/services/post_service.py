from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from typing import Optional, List
from app.models import Post, User, Like
from app.schemas import PostCreate
from app.services.base_service import BaseService

class PostService(BaseService[Post]):
    def __init__(self):
        super().__init__(Post)

    def get_post_by_id(self, db: Session, post_id: int, user_id: int):
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

    def get_all_posts(self, db: Session, limit: int = 10, search: Optional[str] = "", current_user: User = None) -> List[Post]:
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

    def create_post(self, db: Session, content: str, published: bool, image_url: str, current_user: User) -> Post:
        return self.create(db, {
            "owner_id": current_user.id,
            "image_url": image_url,
            "content": content,
            "published": published,
            "likes": 0,
        })

    def delete_post(self, db: Session, post_id: int, current_user: User) -> Optional[bool]:
        post = self.get_by_id(db, post_id)
        if not post:
            return None 
        if post.owner_id != current_user.id:
            return False 
        return self.delete(db, post_id)

    def update_post(self, db: Session, post_id: int, post_data: PostCreate, current_user: User) -> Optional[bool]:
        post = self.get_by_id(db, post_id)
        if not post:
            return None 
        if post.owner_id != current_user.id:
            return False 
        return self.update(db, post_id, post_data.dict())
