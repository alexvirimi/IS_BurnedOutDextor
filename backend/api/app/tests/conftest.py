# Configuración de tests: DB en memoria, cliente HTTP, fixtures de usuarios por rol.

import pytest
import uuid
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
from app.deps.auth_deps import get_current_user
from app.schemas.auth_scheme import CurrentUserData

# ============================================================
# TEST DATABASE (SQLite en memoria)
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
# CREAR TABLAS UNA SOLA VEZ POR SESIÓN
# ============================================================

@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ============================================================
# FIXTURE DE DB: una transacción por test, rollback al final
# ============================================================

@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# ============================================================
# FIXTURE DE CLIENT: inyecta la db de test
# ============================================================

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

# ============================================================
# FIXTURE: usuario RRHH (nivel 3)
# ============================================================

@pytest.fixture
def rrhh_user(db):
    rank = Rank(id=uuid.uuid4(), rank_name="rrhh", level=3)
    area = Area(id=uuid.uuid4(), name="RRHH")
    group = Group(id=uuid.uuid4(), name="RRHH Team", id_area=area.id, id_leader=None)
    worker = Worker(
        id=uuid.uuid4(), name="Admin", last_names="RRHH",
        age=30, gender="M", id_group=group.id, id_rank=rank.id, flag=False
    )
    auth_user = AuthUser(
        id=uuid.uuid4(), worker_id=worker.id,
        username="adminrrhh", password="1234"
    )

    db.add_all([rank, area, group, worker, auth_user])
    db.flush()

    current_user = CurrentUserData(
        auth_user_id=auth_user.id,
        worker_id=worker.id,
        username=auth_user.username,
        rank_level=3,
        rank_name="rrhh",
        id_group=group.id
    )

    app.dependency_overrides[get_current_user] = lambda: current_user

    yield current_user

    app.dependency_overrides.pop(get_current_user, None)


# ============================================================
# FIXTURE: usuario líder (nivel 2)
# ============================================================

@pytest.fixture
def leader_user(db):
    rank = Rank(id=uuid.uuid4(), rank_name="lider", level=2)
    area = Area(id=uuid.uuid4(), name="TI")
    group = Group(id=uuid.uuid4(), name="Backend", id_area=area.id, id_leader=None)
    worker = Worker(
        id=uuid.uuid4(), name="Leader", last_names="Test",
        age=30, gender="M", id_group=group.id, id_rank=rank.id, flag=False
    )
    auth_user = AuthUser(
        id=uuid.uuid4(), worker_id=worker.id,
        username="leader", password="1234"
    )

    db.add_all([rank, area, group, worker, auth_user])
    db.flush()

    current_user = CurrentUserData(
        auth_user_id=auth_user.id,
        worker_id=worker.id,
        username="leader",
        rank_level=2,
        rank_name="lider",
        id_group=group.id
    )

    app.dependency_overrides[get_current_user] = lambda: current_user

    yield current_user

    app.dependency_overrides.pop(get_current_user, None)
