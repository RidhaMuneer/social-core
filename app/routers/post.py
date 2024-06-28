from typing import List, Optional
from fastapi import (
    status,
    HTTPException,
    Depends,
    APIRouter,
    Response,
    File,
    UploadFile,
    Form,
)
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
from ..schemas import PostResponse, PostCreate, User
from ..oauth2 import get_current_user
import boto3
from ..config import Settings
from ..utils import generate_random_url

settings = Settings()

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
BUCKET_NAME = settings.bucket_name

router = APIRouter(prefix="/app/posts", tags=["Posts"])


@router.get("/", response_model=List[PostResponse])
def get_posts(
    db: Session = Depends(get_db), limit: int = 10, search: Optional[str] = ""
):
    posts_with_likes_and_users = (
        db.query(
            models.Post,
            func.count(models.Like.post_id).label("like_count"),
            models.User,
        )
        .outerjoin(models.Like, models.Like.post_id == models.Post.id)
        .join(models.User, models.User.id == models.Post.owner_id)
        .group_by(models.Post.id, models.User.id)
        .filter(models.Post.content.contains(search))
        .order_by(models.Post.created_at.desc())
        .limit(limit)
        .all()
    )

    results = [
        PostResponse(
            id=post.id,
            content=post.content,
            published=post.published,
            image_url=post.image_url,
            created_at=post.created_at,
            owner_id=post.owner_id,
            like_count=like_count,
            owner=User(id=user.id, username=user.username, image_url=user.image_url),
        )
        for post, like_count, user in posts_with_likes_and_users
    ]

    return results


@router.get("/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post_with_likes_and_user = (
        db.query(models.Post, func.count(models.Like.post_id).label("like_count"), models.User)
        .outerjoin(models.Like, models.Like.post_id == models.Post.id)
        .join(models.User, models.User.id == models.Post.owner_id)
        .group_by(models.Post.id, models.User.id)
        .order_by(models.Post.created_at.desc())
        .filter(models.Post.id == id)
        .first()
    )

    if not post_with_likes_and_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    post, like_count, user = post_with_likes_and_user

    response_post = PostResponse(
        id=post.id,
        content=post.content,
        published=post.published,
        image_url=post.image_url,
        created_at=post.created_at,
        owner_id=post.owner_id,
        like_count=like_count,
        owner=User(
            id=user.id,
            username=user.username,
            image_url=user.image_url
        ),
    )
    return response_post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(
    content: str = Form(...),
    published: bool = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    image_url = generate_random_url(10)
    new_post = models.Post(
        owner_id=current_user.id,
        image_url=settings.image_url_domain + image_url,
        content=content,
        published=published,
    )
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    s3.upload_fileobj(file.file, BUCKET_NAME, image_url)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    response_post = PostResponse(
        id=new_post.id,
        content=new_post.content,
        published=new_post.published,
        image_url=new_post.image_url,
        created_at=new_post.created_at,
        owner_id=new_post.owner_id,
        like_count=0,
        owner=User(
            id=user.id,
            username=user.username,
            image_url=user.image_url,
        )
    )
    return response_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    deleted_post = db.query(models.Post).filter(models.Post.id == id)
    if not deleted_post.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with {id} doesn't exit"
        )
    if deleted_post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=PostResponse)
def update_post(
    id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    updated_post_query = db.query(models.Post).filter(models.Post.id == id)
    post_query = updated_post_query.first()

    if not post_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} doesn't exist",
        )

    if post_query.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not allowed")

    updated_post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    post_with_likes = (
        db.query(models.Post, func.count(models.Like.post_id).label("like_count"))
        .outerjoin(models.Like, models.Like.post_id == models.Post.id)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )

    if not post_with_likes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} doesn't exist",
        )

    post, like_count = post_with_likes

    response_post = PostResponse(
        id=post.id,
        content=post.content,
        published=post.published,
        image_url=post.image_url,
        created_at=post.created_at,
        owner_id=post.owner_id,
        like_count=like_count,
    )

    return response_post
