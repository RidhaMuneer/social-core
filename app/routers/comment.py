from fastapi import status, Depends, APIRouter
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas import Comment, User
from app.oauth2 import get_current_user
from app.controllers.comment_controller import CommentController

router = APIRouter(prefix="/app/comment", tags=["Comment"])

@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_comments(id: int, db: Session = Depends(get_db)):
    return CommentController.get_comments(id, db)

@router.post("/", status_code=status.HTTP_201_CREATED)
def comment(
    comment: Comment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommentController.create_comment(comment, db, current_user)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CommentController.delete_comment(id, db, current_user)