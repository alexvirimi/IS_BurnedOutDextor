from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Obtiene la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
