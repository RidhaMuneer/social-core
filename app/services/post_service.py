from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from app.models import Post, User, Like
from typing import Optional
from app.schemas import PostCreate

def get_post_by_id(post_id: int, user_id: int, db: Session):
    post_with_users = (
        db.query(
            Post,
            User.id,
            User.username,
            User.image_url,
            exists().where((Like.post_id == Post.id) & (Like.user_id == user_id)).label("isLiked")
        )
        .join(User, User.id == Post.owner_id)
        .filter(Post.id == post_id)
        .filter(Post.published)
        .first()
    )

    return post_with_users

def get_all_posts_and_search(db: Session, limit: int = 10, search: Optional[str] = "", current_user: User = None):    
    posts_with_users = (
        db.query(
            Post,
            User.id,
            User.username,
            User.image_url,
            exists().where((Like.post_id == Post.id) & (Like.user_id == current_user.id)).label("isLiked")
        )
        .join(User, User.id == Post.owner_id)
        .group_by(Post.id, User.id)
        .filter(Post.content.contains(search))
        .filter(Post.published)
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )

    return posts_with_users

def create_post_service(content: str, published: bool, db: Session, image_url: str, current_user: User):
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

def delete_post_service(id: int, db: Session, current_user: User):
    deleted_post_query = db.query(Post).filter(Post.id == id)
    deleted_post = deleted_post_query.first()

    if not deleted_post:
        return None 

    if deleted_post.owner_id != current_user.id:
        return False 

    deleted_post_query.delete(synchronize_session=False)
    db.commit()
    return True 

def update_post_service(post: PostCreate, db: Session, current_user: User, id: int):
    updated_post_query = db.query(Post).filter(Post.id == id)
    updated_post = updated_post_query.first()

    if not updated_post:
        return None 

    if updated_post.owner_id != current_user.id:
        return False 

    updated_post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return True