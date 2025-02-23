from sqlalchemy.orm import Session
from app.services.comment_service import CommentService
from app.schemas import Comment, User
from fastapi import HTTPException, status, Response

class CommentController:
    @staticmethod
    def get_comments(id: int, db: Session):
        comments = CommentService.get_comments(id, db)

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

    @staticmethod
    def create_comment(comment: Comment, db: Session, current_user: User):
        new_comment, owner = CommentService.create_comment(comment, db, current_user)

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

    @staticmethod
    def delete_comment(id: int, db: Session, current_user: User):
        comment = CommentService.create_comment(id, db, current_user)

        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
            )
    
        if comment is False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    
        return Response(status_code=status.HTTP_204_NO_CONTENT)