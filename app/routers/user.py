from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.controllers.user_controller import UserController
from app.oauth2 import get_current_user
from typing import List, Optional
from app.schemas import UserResponse, User

router = APIRouter(prefix="/app", tags=["Users"])

@router.get("/user")
def get_current_user_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return UserController.get_user_profile(db, current_user.id)

@router.get("/user/{id}")
def get_user_by_id(
    id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return UserController.get_user_profile_with_posts(db, id, current_user)

@router.get("/user/{id}/followers", response_model=List[UserResponse])
def get_user_followers(id: int, db: Session = Depends(get_db)):
    return UserController.get_user_followers(db, id)

@router.get("/user/{id}/followings", response_model=List[UserResponse])
def get_user_followings(id: int, db: Session = Depends(get_db)):
    return UserController.get_user_followings(db, id)

@router.get("/users/search/", response_model=List[User])
def search_users(search: Optional[str] = "", db: Session = Depends(get_db)):
    return UserController.search_users(db, search)

@router.get("/users/suggestions", response_model=List[User])
def get_user_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 3
):
    return UserController.get_user_suggestions(db, current_user.id, limit)
