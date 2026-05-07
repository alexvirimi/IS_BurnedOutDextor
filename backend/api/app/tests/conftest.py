# app/tests/conftest.py

import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.dbmodels.base import Base

# ============================================================
# TEST DATABASE
# ============================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================
# OVERRIDE DB
# ============================================================

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ============================================================
# CLIENT FIXTURE
# ============================================================

@pytest.fixture(scope="function")
def client():

    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)

# ============================================================
# DB FIXTURE
# ============================================================

@pytest.fixture(scope="function")
def db():

    Base.metadata.create_all(bind=engine)

    database = TestingSessionLocal()

    try:
        yield database

    finally:
        database.close()

    Base.metadata.drop_all(bind=engine)