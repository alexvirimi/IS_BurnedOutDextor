# app/unirepository.py

from typing import Type, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session

T = TypeVar('T')

class UniversalRepository:
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_all(self) -> List[Any]:
        return self.db.query(self.model).all()

    def get_by_id(self, obj_id: Any) -> Optional[Any]:
        return self.db.query(self.model).get(obj_id)

    def create(self, data: dict) -> Any:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj