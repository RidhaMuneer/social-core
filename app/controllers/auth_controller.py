from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.oauth2 import create_access_token
from app.utils import Utils

class AuthController:
    @staticmethod
    def login_user(email: str, password: str, db: Session):
        user = UserService.get_user_by_email(db, email)
        if not user or not Utils.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
            )
    
        access_token = create_access_token(data={"user_id": user.id})
        return {"access_token": access_token}

    @staticmethod
    def register_user(username: str, email: str, password: str, file, db: Session):
        if UserService.get_user_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User already exists"
            )
    
        if UserService.get_user_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Username is taken"
            )
    
        new_user = UserService.create_user(db, username, email, password, file)
        access_token = create_access_token(data={"user_id": new_user.id})
        return {"access_token": access_token}
