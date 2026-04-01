"""
📝 ARCHIVO DE PRUEBA
Este archivo contiene operaciones CRUD para la tabla Area.
Úsalo en endpoints para crear, leer, actualizar y eliminar areas.
⚠️ Si cambias la lógica de Area, actualiza estos controladores.
"""

from sqlalchemy.orm import Session
from logic.schemas.area import AreaCreate
from app.models.area import Area


def create_area(session: Session, area_create: AreaCreate) -> Area:
    """
    Crear una nueva area en la base de datos.
    
    Args:
        session: Sesión de SQLAlchemy
        area_create: Esquema con datos de la area
    
    Returns:
        Objeto Area creado
    """
    db_area = Area(name=area_create.name)
    session.add(db_area)
    session.commit()
    session.refresh(db_area)
    return db_area


def get_area(session: Session, area_id: str) -> Area | None:
    """Obtener un area por ID"""
    return session.query(Area).filter(Area.id == area_id).first()


def get_all_areas(session: Session) -> list[Area]:
    """Obtener todas las areas"""
    return session.query(Area).all()


def update_area(session: Session, area_id: str, area_update) -> Area | None:
    """Actualizar un area"""
    db_area = session.query(Area).filter(Area.id == area_id).first()
    if db_area:
        if area_update.name:
            db_area.name = area_update.name
        session.commit()
        session.refresh(db_area)
    return db_area


def delete_area(session: Session, area_id: str) -> bool:
    """Eliminar un area"""
    db_area = session.query(Area).filter(Area.id == area_id).first()
    if db_area:
        session.delete(db_area)
        session.commit()
        return True
    return False
