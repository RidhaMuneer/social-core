from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.models import User

user_service = UserService()

class UserController:
    @staticmethod
    def get_user_profile(db: Session, user_id: int):
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} does not exist",
            )

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "image_url": user.image_url,
            "follower_count": user_service.get_follower_count(db, user.id),
            "following_count": user_service.get_following_count(db, user.id),
            "posts": user_service.get_user_posts(db, user.id)
        }

    @staticmethod
    def get_user_profile_with_posts(db: Session, user_id: int, current_user: User):
        user = user_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} does not exist",
            )

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "image_url": user.image_url,
            "follower_count": user_service.get_follower_count(db, user.id),
            "following_count": user_service.get_following_count(db, user.id),
            "posts": user_service.get_user_posts_with_likes(db, user.id, current_user.id)
        }

    @staticmethod
    def get_user_followers(db: Session, user_id: int):
        return user_service.get_followers(db, user_id)

    @staticmethod
    def get_user_followings(db: Session, user_id: int):
        return user_service.get_followings(db, user_id)

    @staticmethod
    def search_users(db: Session, search: str):
        return user_service.search_users(db, search)

    @staticmethod
    def get_user_suggestions(db: Session, current_user_id: int, limit: int = 3):
        return user_service.get_user_suggestions(db, current_user_id, limit)
