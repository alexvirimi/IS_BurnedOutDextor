# app/unirepository.py

from typing import Type, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session

T = TypeVar('T')

class UniversalRepository:
    def __init__(self, model: Type[T], db: Session) -> None:
        self.model = model
        self.db = db
        
    def get_all(self) -> List[Any]:
        return self.db.query(self.model).all()
    
    def get_by_id(self, obj_id: Any) -> Optional[Any]:
        return self.db.query(self.model).get(obj_id)  # Solo funciona porque ID es la primary key en todas las tablas
    
    def create(self, data: dict) -> Any:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj_id: Any, data: dict) -> Optional[Any]:
        obj = self.db.query(self.model).get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def delete_by_id(self, obj_id: Any) -> bool:
        obj = self.db.query(self.model).get(obj_id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
    
    # Puede que se elimine a futuro, porque realmente la función de eliminar todo no tiene sentido.
    # Es por pruebas mientras testeamos la base de datos añadiendo y quitando datos.
    
    def delete_all(self) -> List[Any]:
        objs = self.db.query(self.model).all()
        for obj in objs:
            self.db.delete(obj)
        self.db.commit()
        return objs