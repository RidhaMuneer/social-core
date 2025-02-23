from sqlalchemy.orm import Session
from app.models import User
from app.utils import Utils
from app.config import Settings
import boto3
from sqlalchemy import func
import random
from app import models

settings = Settings()
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
BUCKET_NAME = settings.bucket_name

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_follower_count(db: Session, user_id: int):
        return db.query(models.Follower).filter(models.Follower.following_id == user_id).count()

    @staticmethod
    def get_following_count(db: Session, user_id: int):
        return db.query(models.Follower).filter(models.Follower.follower_id == user_id).count()

    @staticmethod
    def get_user_posts(db: Session, user_id: int):
        return db.query(models.Post).filter(models.Post.owner_id == user_id).all()

    @staticmethod
    def get_user_posts_with_likes(db: Session, user_id: int, current_user_id: int):
        posts_with_likes = db.query(models.Post).filter(models.Post.owner_id == user_id).order_by(models.Post.created_at.desc()).all()

        posts = []
        for post in posts_with_likes:
            is_liked = db.query(models.Like).filter(
                models.Like.post_id == post.id, models.Like.user_id == current_user_id
            ).first() is not None

            posts.append({
                "id": post.id,
                "content": post.content,
                "image_url": post.image_url,
                "published": post.published,
                "created_at": post.created_at,
                "like_count": post.likes,
                "is_liked": is_liked
            })

        return posts

    @staticmethod
    def get_followers(db: Session, user_id: int):
        return db.query(models.User).join(
            models.Follower, models.Follower.follower_id == models.User.id
        ).filter(models.Follower.following_id == user_id).all()

    @staticmethod
    def get_followings(db: Session, user_id: int):
        return db.query(models.User).join(
            models.Follower, models.Follower.following_id == models.User.id
        ).filter(models.Follower.follower_id == user_id).all()

    @staticmethod
    def search_users(db: Session, search: str):
        query = db.query(models.User.id, models.User.username, models.User.image_url)
        if search:
            query = query.filter(func.lower(models.User.username).contains(func.lower(search)))
        return query.all()

    @staticmethod
    def get_user_suggestions(db: Session, current_user_id: int, limit: int = 3):
        following_ids = db.query(models.Follower.following_id).filter(
            models.Follower.follower_id == current_user_id
        ).all()
        following_ids = [f.following_id for f in following_ids]

        suggestions = db.query(models.User).filter(
            models.User.id != current_user_id, ~models.User.id.in_(following_ids)
        ).all()

        if len(suggestions) > limit:
            suggestions = random.sample(suggestions, limit)

        return suggestions
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, file):
        hashed_password = Utils.hash(password)
        image_url = Utils.generate_random_url(10)
        s3.upload_fileobj(file.file, BUCKET_NAME, image_url)

        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            image_url=f"{settings.image_url_domain}{image_url}",
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
