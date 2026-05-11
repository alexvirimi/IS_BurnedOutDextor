import uuid
import pytest
import bcrypt

from app.servicemodels.auth_user_service import AuthUserService

from app.dbmodels.auth_user import AuthUser
from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker


@pytest.fixture
def auth_data(db):

    rank = Rank(
        id=uuid.uuid4(),
        rank_name="Empleado",
        level=1
    )

    area = Area(
        id=uuid.uuid4(),
        name="Tecnología"
    )

    group = Group(
        id=uuid.uuid4(),
        name="Backend",
        id_area=area.id,
        id_leader=None
    )

    worker = Worker(
        id=uuid.uuid4(),
        name="Mario",
        last_names="Julio",
        age=20,
        gender="M",
        id_group=group.id,
        id_rank=rank.id
    )

    db.add_all([
        rank,
        area,
        group,
        worker
    ])

    db.commit()

    return {
        "worker": worker,
        "group": group,
        "rank": rank
    }


def test_register_user(db, auth_data):

    service = AuthUserService(db)

    payload = {
        "worker_id": auth_data["worker"].id,
        "username": "mario",
        "password": "123456"
    }

    created = service.register_user(payload)

    assert created.id is not None
    assert created.username == "mario"

    assert bcrypt.checkpw(
        "123456".encode("utf-8"),
        created.password.encode("utf-8")
    )


def test_login_user_success(db, auth_data):

    service = AuthUserService(db)

    created = service.register_user({
        "worker_id": auth_data["worker"].id,
        "username": "admin",
        "password": "123456"
    })

    auth_user = service.login_user(
        username="admin",
        password="123456"
    )

    assert auth_user is not None
    assert auth_user.id == created.id


def test_login_user_invalid_password(db, auth_data):

    service = AuthUserService(db)

    service.register_user({
        "worker_id": auth_data["worker"].id,
        "username": "admin",
        "password": "123456"
    })

    auth_user = service.login_user(
        username="admin",
        password="wrongpassword"
    )

    assert auth_user is None


def test_login_user_not_found(db):

    service = AuthUserService(db)

    auth_user = service.login_user(
        username="ghost",
        password="123456"
    )

    assert auth_user is None


def test_get_auth_user_by_id(db, auth_data):

    service = AuthUserService(db)

    created = service.register_user({
        "worker_id": auth_data["worker"].id,
        "username": "mario",
        "password": "123456"
    })

    found = service.get_auth_user_by_id(created.id)

    assert found is not None
    assert found.id == created.id


def test_get_auth_user_with_worker_info(db, auth_data):

    service = AuthUserService(db)

    created = service.register_user({
        "worker_id": auth_data["worker"].id,
        "username": "mario",
        "password": "123456"
    })

    result = service.get_auth_user_with_worker_info(created.id)

    assert result is not None
    assert result["username"] == "mario"
    assert result["rank_level"] == 1
    assert result["rank_name"] == "Empleado"


def test_username_exists(db, auth_data):

    service = AuthUserService(db)

    service.register_user({
        "worker_id": auth_data["worker"].id,
        "username": "existinguser",
        "password": "123456"
    })

    exists = service.username_exists("existinguser")

    assert exists is True


def test_username_not_exists(db):

    service = AuthUserService(db)

    exists = service.username_exists("ghostuser")

    assert exists is False