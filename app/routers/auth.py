from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.controllers.auth_controller import AuthController
from app.schemas import Token

router = APIRouter(prefix="/app", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    return AuthController.login_user(email, password, db)

@router.post("/register", response_model=Token)
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return AuthController.register_user(username, email, password, file, db)
