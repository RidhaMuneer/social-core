from sqlalchemy.orm import Session
from app.models import Comment, User, Post
from app.schemas import Comment as CommentSchema, User as UserSchema

class CommentService:
    @staticmethod
    def get_comments(id: int, db: Session):
        comments_with_users = (
            db.query(Comment, User)
            .join(User, Comment.owner_id == User.id)
            .filter(Comment.post_id == id).order_by(Comment.created_at.desc())
            .all()
        )

        return comments_with_users

    @staticmethod
    def create_comment(comment: CommentSchema, db: Session, current_user: UserSchema):
        post = db.query(Post).filter(Post.id == comment.post_id).first()
        if not post:
            return None
    
        new_comment = Comment(
            post_id=comment.post_id,
            content=comment.content,
            owner_id=current_user.id,
        )

        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)

        owner = db.query(User).filter(User.id == new_comment.owner_id).first()

        return new_comment, owner

    @staticmethod
    def delete_comment(id: int, db: Session, current_user: UserSchema):
        comment = db.query(Comment).filter(Comment.id == id).first()
        if not comment:
            return None
        if comment.user_id != current_user.id:
            raise False
        comment.delete(synchronize_session=False)
        db.commit()

        return True