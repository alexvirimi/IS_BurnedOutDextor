import os
from functools import lru_cache


class Settings:
    """Configuración de la aplicación"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/inbudex"
    )
    
    # SQLAlchemy settings
    SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"
    SQLALCHEMY_POOL_SIZE: int = int(os.getenv("SQLALCHEMY_POOL_SIZE", "5"))
    SQLALCHEMY_POOL_RECYCLE: int = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600"))
    
    # Superuser (admin default)
    FIRST_SUPERUSER: str = os.getenv("FIRST_SUPERUSER", "admin@inbudex.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")


@lru_cache()
def get_settings() -> Settings:
    """Obtener configuración cacheada"""
    return Settings()


settings = get_settings()
