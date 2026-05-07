import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL")

SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"
SQLALCHEMY_POOL_SIZE: int = int(os.getenv("SQLALCHEMY_POOL_SIZE", "5"))
SQLALCHEMY_POOL_RECYCLE: int = int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600"))