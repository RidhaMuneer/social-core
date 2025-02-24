from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic, List, Optional
from app.models import Base

T = TypeVar("T", bound=Base)

class BaseService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, obj_id: int) -> Optional[T]:
        return db.query(self.model).filter(self.model.id == obj_id).first()

    def get_all(self, db: Session, limit: int = 10, skip: int = 0) -> List[T]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_data: dict) -> T:
        obj = self.model(**obj_data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, obj_id: int, update_data: dict) -> Optional[T]:
        obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if not obj:
            return None
        for key, value in update_data.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, obj_id: int) -> bool:
        obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True
