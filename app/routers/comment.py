from fastapi import status, HTTPException, Depends, APIRouter, Response
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models
from ..schemas import Comment
from ..oauth2 import get_current_user

router = APIRouter(prefix="/app/comment", tags=["Comment"])

@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_comments(id: int, db: Session = Depends(get_db)):
    comments_with_users = (
        db.query(models.Comment, models.User)
        .join(models.User, models.Comment.owner_id == models.User.id)
        .filter(models.Comment.post_id == id)
        .all()
    )

    return [
        {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "post_id": comment.post_id,
            "owner_id": comment.owner_id,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "image_url": user.image_url if hasattr(user, "image_url") else None
            }
        }
        for comment, user in comments_with_users
    ]

@router.post("/", status_code=status.HTTP_201_CREATED)
def comment(
    comment: Comment,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    
    new_comment = models.Comment(
        post_id=comment.post_id,
        content=comment.content,
        owner_id=current_user.id,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    owner = db.query(models.User).filter(models.User.id == new_comment.owner_id).first()
    return {
        "content": new_comment.content,
        "created_at": new_comment.created_at,
        "owner_username": owner.username,
        "owner_image_url": owner.image_url
    }


@router.delete("/{id}", status_code=status.HTTP_201_CREATED)
def delete_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
        )
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    comment.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)