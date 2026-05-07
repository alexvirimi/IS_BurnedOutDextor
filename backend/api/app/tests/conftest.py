# app/tests/conftest.py

import pytest
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.dbmodels.base import Base
from app.dbmodels.auth_user import AuthUser
from app.dbmodels.ranks import Rank
from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.workers import Worker
from app.dbmodels.auth_user import AuthUser
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from app.main import app
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



@pytest.fixture
def rrhh_user(db):

    # Crear rank RRHH
    rank = Rank(
        id=uuid.uuid4(),
        rank_name="rrhh",
        level=3
    )

    # Crear área
    area = Area(
        id=uuid.uuid4(),
        name="RRHH"
    )

    # Crear grupo
    group = Group(
        id=uuid.uuid4(),
        name="RRHH Team",
        id_area=area.id,
        id_leader=None
    )

    # Crear worker RRHH
    worker = Worker(
        id=uuid.uuid4(),
        name="Admin",
        last_names="RRHH",
        age=30,
        gender="M",
        id_group=group.id,
        id_rank=rank.id,
        flag=False
    )

    # Crear auth user
    auth_user = AuthUser(
        id=uuid.uuid4(),
        worker_id=worker.id,
        username="adminrrhh",
        password="1234"
    )

    db.add_all([rank, area, group, worker, auth_user])
    db.commit()

    current_user = CurrentUserData(
        auth_user_id=auth_user.id,
        worker_id=worker.id,
        username=auth_user.username,
        rank_level=3,
        rank_name="rrhh",
        id_group=group.id
    )

    # Override auth dependency
    app.dependency_overrides[require_rrhh] = lambda: current_user

    yield current_user

    app.dependency_overrides.clear()