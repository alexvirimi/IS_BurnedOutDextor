#Archivo de configuracion para los test, es super importante porque crea una DB de prueba y un cliente de test para hacer las peticiones a la API. 
#Tambien tiene fixtures para crear usuarios de prueba con diferentes roles, para la validacion de la autenticacion y autorizacion en los endpoints. 
#Esencial para asegurar que los tests sean independientes y no afecten la DB real.

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
from app.deps.auth_deps import get_current_user


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
# CREATE TABLES ONCE
# ============================================================

@pytest.fixture(scope="session", autouse=True)
def prepare_database():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

# ============================================================
# DB SESSION FIXTURE
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
# CLIENT FIXTURE
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

    rank = Rank(
        id=uuid.uuid4(),
        rank_name="rrhh",
        level=3
    )

    area = Area(
        id=uuid.uuid4(),
        name="RRHH"
    )

    group = Group(
        id=uuid.uuid4(),
        name="RRHH Team",
        id_area=area.id,
        id_leader=None
    )

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

    auth_user = AuthUser(
        id=uuid.uuid4(),
        worker_id=worker.id,
        username="adminrrhh",
        password="1234"
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

    from app.deps.auth_deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: current_user

    yield current_user

    app.dependency_overrides.clear()
    
@pytest.fixture
def leader_user(db):

    rank = Rank(
        id=uuid.uuid4(),
        rank_name="lider",
        level=2
    )

    area = Area(
        id=uuid.uuid4(),
        name="TI"
    )

    group = Group(
        id=uuid.uuid4(),
        name="Backend",
        id_area=area.id,
        id_leader=None
    )

    worker = Worker(
        id=uuid.uuid4(),
        name="Leader",
        last_names="Test",
        age=30,
        gender="M",
        id_group=group.id,
        id_rank=rank.id,
        flag=False
    )

    auth_user = AuthUser(
        id=uuid.uuid4(),
        worker_id=worker.id,
        username="leader",
        password="1234"
    )

    db.add_all([rank, area, group, worker, auth_user])
    db.commit()

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

    app.dependency_overrides.clear()