from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Form
# from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..utils import generate_random_url, verify, hash
from ..oauth2 import create_access_token
from ..schemas import Token, UserLogin
from ..config import Settings
import boto3

settings = Settings()

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
)
BUCKET_NAME = settings.bucket_name

router = APIRouter(prefix="/app", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invaild Credentials"
        )
    if not verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invaild Credentials"
        )
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Token)
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User already exits"
        )
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Username is taken"
        )
    hashed_password = hash(password)
    image_url = generate_random_url(10)
    s3.upload_fileobj(file.file, BUCKET_NAME, image_url)
    new_user = User(
        username=username, email=email, password=hashed_password, image_url=settings.image_url_domain + image_url
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(data={"user_id": new_user.id})
    return {"access_token": access_token}
