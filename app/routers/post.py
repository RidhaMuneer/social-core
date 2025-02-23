from typing import List, Optional
from fastapi import (
    status,
    Depends,
    APIRouter,
    File,
    UploadFile,
    Form,
)
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import PostResponse, PostCreate
from app.oauth2 import get_current_user
from app.controllers.post_controller import PostController

router = APIRouter(prefix="/app/posts", tags=["Posts"])

@router.get("/", response_model=List[PostResponse])
def get_posts(
    db: Session = Depends(get_db), limit: int = 10, search: Optional[str] = "", current_user: User = Depends(get_current_user)
):
    return PostController.get_all_posts(db, current_user, limit, search)

@router.get("/{id}")
def get_post(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return PostController.get_one_post(id, db, current_user)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(
    content: str = Form(...),
    published: bool = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PostController.create_post(content, published, file, db, current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PostController.delete_post(id, db, current_user)

@router.put("/{id}", status_code=status.HTTP_200_OK)
def update_post(
    id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return PostController.update_post(id, post, db, current_user)