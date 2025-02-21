from fastapi import HTTPException, status, Depends, UploadFile, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import User, PostResponse, PostCreate
from app.services.post_service import get_post_by_id, get_all_posts_and_search, create_post_service, delete_post_service, update_post_service
from app.oauth2 import get_current_user
from typing import Optional
import boto3
from app.config import Settings
from app.utils import generate_random_url

settings = Settings()

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
BUCKET_NAME = settings.bucket_name

def get_one_post(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    post_with_users = get_post_by_id(id, current_user.id, db)

    if not post_with_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )

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
        owner=User(
            id=user_id,
            username=username,
            image_url=image_url
        )
    )

def get_all_posts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), limit: int = 10, search: Optional[str] = ""):
    posts_with_users = get_all_posts_and_search(db, limit, search, current_user)

    results = [
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

    return results

def create_post(content: str, published: bool, file: UploadFile, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    url = generate_random_url(10)
    image_url = settings.image_url_domain + url
    create_post_service(content, published, db, image_url, current_user)
    s3.upload_fileobj(file.file, BUCKET_NAME, url)
    return Response(status_code=status.HTTP_200_OK)

def delete_post_controller(id: int, db: Session, current_user: User):
    deleted_post = delete_post_service(id, db, current_user)
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} doesn't exit"
        )
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    if deleted_post:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

def update_post_controler(id: int, post: PostCreate, db: Session, current_user: User):
    updated_post = update_post_service(post, db, current_user, id)

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} doesn't exist",
        )
    
    if updated_post is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    
    if updated_post:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
