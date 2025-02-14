from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    image_url: str
    follower_count: int
    following_count: int

    class Config:
        from_attributes = True


class User(BaseModel):
    id: int
    username: str
    image_url: str

class Comment(BaseModel):
    post_id: int
    content: str

class PostResponse(BaseModel):
    id: int
    content: str
    published: bool
    image_url: str
    created_at: datetime
    isLiked: bool
    owner_id: int
    like_count: int
    owner: User

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    id: Optional[str] = None

    class Config:
        from_attributes = True


class Like(BaseModel):
    post_id: int
    dir: int


class FollowRequest(BaseModel):
    user_id: int
    dir: int
