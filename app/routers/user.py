from sqlalchemy import func
from ..schemas import UserResponse, User
from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models
from typing import List, Optional
from ..oauth2 import get_current_user
import random

router = APIRouter(prefix="/app", tags=["Users"])


@router.get("/user", response_model=UserResponse)
def get_user(
    db: Session = Depends(get_db), current_user: int = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {current_user.id} does not exist",
        )

    follower_count = (
        db.query(models.Follower)
        .filter(models.Follower.following_id == current_user.id)
        .count()
    )
    following_count = (
        db.query(models.Follower)
        .filter(models.Follower.follower_id == current_user.id)
        .count()
    )

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "image_url": user.image_url,
        "follower_count": follower_count,
        "following_count": following_count,
    }


@router.get("/user/{id}", response_model=UserResponse)
def get_user_from_id(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist",
        )

    follower_count = (
        db.query(models.Follower).filter(models.Follower.following_id == id).count()
    )
    following_count = (
        db.query(models.Follower).filter(models.Follower.follower_id == id).count()
    )

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "image_url": user.image_url,
        "follower_count": follower_count,
        "following_count": following_count,
    }


@router.get("/user/{id}/posts")
def get_user_posts(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist",
        )
    posts = db.query(models.Post).filter(models.Post.owner_id == id).all()
    if not posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't have any posts"
        )
    return posts


@router.get("/users/{id}/posts/{post_id}")
def get_user_post(id: int, post_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} does not exist",
        )
    post = (
        db.query(models.Post)
        .filter(models.Post.owner_id == id)
        .filter(models.Post.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't have any posts"
        )
    return post


@router.get("/user/{id}/followers", response_model=List[UserResponse])
def get_followers(id: int, db: Session = Depends(get_db)):
    followers = (
        db.query(models.User)
        .join(models.Follower, models.Follower.follower_id == models.User.id)
        .filter(models.Follower.following_id == id)
        .all()
    )

    return [
        {
            "id": follower.id,
            "username": follower.user_name,
            "email": follower.email,
            "image_url": follower.image_url,
            "follower_count": db.query(models.Follower)
            .filter(models.Follower.following_id == follower.id)
            .count(),
            "following_count": db.query(models.Follower)
            .filter(models.Follower.follower_id == follower.id)
            .count(),
        }
        for follower in followers
    ]


@router.get("/user/{id}/followings", response_model=List[UserResponse])
def get_followings(id: int, db: Session = Depends(get_db)):
    followings = (
        db.query(models.User)
        .join(models.Follower, models.Follower.following_id == models.User.id)
        .filter(models.Follower.follower_id == id)
        .all()
    )

    return [
        {
            "id": following.id,
            "username": following.user_name,
            "email": following.email,
            "image_url": following.image_url,
            "follower_count": db.query(models.Follower)
            .filter(models.Follower.following_id == following.id)
            .count(),
            "following_count": db.query(models.Follower)
            .filter(models.Follower.follower_id == following.id)
            .count(),
        }
        for following in followings
    ]


@router.get("/users/search/", response_model=List[User])
def search_users(search: Optional[str] = "", db: Session = Depends(get_db)):
    if search:
        users = db.query(
            models.User.id,
            models.User.username,
            models.User.image_url
        ).filter(
            func.lower(models.User.username).contains(func.lower(search))
        ).all()
    else:
        users = db.query(
            models.User.id,
            models.User.username,
            models.User.image_url
        ).all()
    return users


@router.get("/users/suggestions", response_model=List[User])
def get_user_suggestions(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
    limit: int = 3
):
    following_ids = db.query(models.Follower.following_id).filter(models.Follower.follower_id == current_user.id).all()
    following_ids = [f.following_id for f in following_ids]

    suggestions = db.query(models.User).filter(models.User.id != current_user.id, ~models.User.id.in_(following_ids)).all()

    if len(suggestions) > limit:
        suggestions = random.sample(suggestions, limit)

    return suggestions