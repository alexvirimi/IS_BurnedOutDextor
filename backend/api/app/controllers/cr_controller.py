# app/unirepository.py

from typing import Type, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session
from uuid import UUID
from app.dbmodels.company import Company
from sqlalchemy import or_
T = TypeVar('T')

class UniversalRepository:
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_all(self) -> List[Any]:
        return self.db.query(self.model).all()

    def get_by_id(self, obj_id: Any) -> Optional[Any]:
        return self.db.get(self.model, obj_id)

    def create(self, data: dict) -> Any:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    def get_by_worker_or_company_id(self, id: UUID):
        return self.db.query(Company).filter(
            or_(
                Company.id == id,
                Company.id_worker == id
            )
        ).first()

