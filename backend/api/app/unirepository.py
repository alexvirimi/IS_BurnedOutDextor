from typing import Type, TypeVar, Generic, List, Optional, Any
from sqlalchemy.orm import Session
from uuid import UUID

# Definimos un tipo genérico que represente a cualquier Modelo
T = TypeVar('T')

class UniversalRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        """
        Al instanciarlo, le pasas el modelo (Area, Group, etc.) 
        y la sesión de la DB.
        """
        self.model = model
        self.db = db

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

    def get_by_id(self, obj_id: Any) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == obj_id).first()

    def create(self, data: dict) -> T:
        # Desempaquetamos el diccionario JSON convertido por FastAPI
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj_id: Any, data: dict) -> Optional[T]:
        obj = self.get_by_id(obj_id)
        if obj:
            for key, value in data.items():
                # setattr cambia el valor de la columna dinámicamente
                if hasattr(obj, key):
                    setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def delete(self, obj_id: Any) -> bool:
        obj = self.get_by_id(obj_id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False