from sqlalchemy.orm import Session
from app.models import Comment, User
from app.schemas import Comment as CommentSchema, User as UserSchema
from app.services.post_service import PostService
from app.services.user_service import UserService
from app.services.base_service import BaseService

post_service = PostService()
user_Service = UserService()

class CommentService(BaseService[Comment]):
    def __init__(self):
        super().__init__(Comment)

    def get_comments(self, db: Session, post_id: int):
        comments_with_users = (
            db.query(Comment, User)
            .join(User, Comment.owner_id == User.id)
            .filter(Comment.post_id == post_id).order_by(Comment.created_at.desc())
            .all()
        )

        return comments_with_users

    def create_comment(self, db: Session, comment: CommentSchema, current_user: UserSchema):
        post = post_service.get_by_id(db, comment.post_id)
        if not post:
            return None
    
        new_comment = self.create(db, {
            "post_id": comment.post_id,
            "content": comment.content,
            "owner_id": current_user.id,
        })

        owner = user_Service.get_user_by_id(db, new_comment.owner_id)
        return new_comment, owner

    def delete_comment(self, db: Session, comment_id: int, current_user: UserSchema):
        comment = self.get_by_id(db, comment_id)
        if not comment:
            return None
        if comment.owner_id != current_user.id:
            return False
        
        return self.delete(db, comment_id)
