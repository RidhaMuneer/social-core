from typing import Optional
from fastapi import HTTPException, status, Depends, UploadFile, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import User, PostResponse, PostCreate
from app.oauth2 import get_current_user
import boto3
from app.config import Settings
from app.utils import Utils
from app.services.post_service import PostService

settings = Settings()
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
BUCKET_NAME = settings.bucket_name

post_service = PostService()

class PostController:
    @staticmethod
    def get_one_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        post_with_users = post_service.get_post_by_id(db, post_id, current_user.id)
        if not post_with_users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} was not found")
        post, user_id, username, image_url, is_liked = post_with_users
        return PostResponse(
            id=post.id,
            content=post.content,
            published=post.published,
            image_url=post.image_url,
            created_at=post.created_at,
            owner_id=post.owner_id,
            like_count=post.likes,
            isLiked=is_liked,
            owner=User(id=user_id, username=username, image_url=image_url)
        )

    @staticmethod
    def get_all_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = 10, search: Optional[str] = ""):
        posts_with_users = post_service.get_all_posts(db, limit, search, current_user)
        return [
            PostResponse(
                id=post.id,
                content=post.content,
                published=post.published,
                image_url=post.image_url,
                created_at=post.created_at,
                owner_id=post.owner_id,
                isLiked=isLiked,
                like_count=post.likes,
                owner=User(id=user_id, username=username, image_url=image_url),
            )
            for post, user_id, username, image_url, isLiked in posts_with_users
        ]

    @staticmethod
    def create_post(content: str, published: bool, file: UploadFile, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        url = Utils.generate_random_url(10)
        image_url = settings.image_url_domain + url
        post_service.create_post(db, content, published, image_url, current_user)
        s3.upload_fileobj(file.file, BUCKET_NAME, url)
        return Response(status_code=status.HTTP_200_OK)

    @staticmethod
    def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        result = post_service.delete_post(db, post_id, current_user)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} doesn't exist")
        if not result:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def update_post(post_id: int, post_data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
        result = post_service.update_post(db, post_id, post_data, current_user)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} doesn't exist")
        if result is False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
