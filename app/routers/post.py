from typing import List, Optional
from fastapi import (
    status,
    Depends,
    APIRouter,
    File,
    UploadFile,
    Form,
)
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models
from app.schemas import PostResponse, PostCreate, User
from app.oauth2 import get_current_user
from app.controllers.post_controller import get_one_post, get_all_posts, create_post, delete_post_controller, update_post_controler


router = APIRouter(prefix="/app/posts", tags=["Posts"])


@router.get("/", response_model=List[PostResponse])
def get_posts(
    db: Session = Depends(get_db), limit: int = 10, search: Optional[str] = "", current_user: models.User = Depends(get_current_user)
):
    return get_all_posts(db, current_user, limit, search)


@router.get("/{id}")
def get_post(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_one_post(id, db, current_user)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(
    content: str = Form(...),
    published: bool = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return create_post(content, published, file, db, current_user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return delete_post_controller(id, db, current_user)


@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_post(
    id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return update_post_controler(id, post, db, current_user)
