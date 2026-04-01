from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import DATABASE_URL, SQLALCHEMY_ECHO, SQLALCHEMY_POOL_SIZE, SQLALCHEMY_POOL_RECYCLE

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=SQLALCHEMY_ECHO,
    pool_size=SQLALCHEMY_POOL_SIZE,
    pool_recycle=SQLALCHEMY_POOL_RECYCLE,
)

# Crear sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """Dependencia para obtener la sesión de BD en FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
