from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL, SQLALCHEMY_ECHO, SQLALCHEMY_POOL_SIZE, SQLALCHEMY_POOL_RECYCLE

engine = create_engine(
    DATABASE_URL,
    echo=SQLALCHEMY_ECHO,
    pool_size=SQLALCHEMY_POOL_SIZE,
    pool_recycle=SQLALCHEMY_POOL_RECYCLE,
    pool_pre_ping=True,   # evita conexiones muertas
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()