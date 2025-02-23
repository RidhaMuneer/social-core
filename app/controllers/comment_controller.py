from sqlalchemy.orm import Session
from app.services.comment_service import get_comments_service, create_comment_service, delete_comment_service
from app.schemas import Comment, User
from fastapi import HTTPException, status, Response

def get_comments_controller(id: int, db: Session):
    comments = get_comments_service(id, db)

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
        for comment, user in comments
    ]

def create_comment_controller(comment: Comment, db: Session, current_user: User):
    new_comment, owner = create_comment_service(comment, db, current_user)

    if new_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    
    return {
        "id": new_comment.id,
        "content": new_comment.content,
        "created_at": new_comment.created_at,
        "user": {
            "id": owner.id,
            "username": owner.username,
            "email": owner.email,
            "image_url": owner.image_url
        }
    }

def delete_comment_controller(id: int, db: Session, current_user: User):
    comment = delete_comment_service(id, db, current_user)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
        )
    
    if comment is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)