import uuid
import pytest

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.auth_user import AuthUser

import bcrypt


@pytest.fixture
def auth_endpoint_data(db):

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


def test_register_success(client, auth_endpoint_data):

    response = client.post(
        "/auth/register",
        data={
            "worker_id": str(auth_endpoint_data["worker"].id),
            "username": "mario",
            "password": "123456"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "mario"
    assert data["worker_id"] == str(auth_endpoint_data["worker"].id)


def test_register_duplicate_username(client, auth_endpoint_data):

    client.post(
        "/auth/register",
        data={
            "worker_id": str(auth_endpoint_data["worker"].id),
            "username": "duplicate",
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/register",
        data={
            "worker_id": str(auth_endpoint_data["worker"].id),
            "username": "duplicate",
            "password": "123456"
        }
    )

    assert response.status_code == 409


def test_register_invalid_worker(client):

    response = client.post(
        "/auth/register",
        data={
            "worker_id": str(uuid.uuid4()),
            "username": "ghost",
            "password": "123456"
        }
    )

    assert response.status_code == 400


def test_login_success(client, auth_endpoint_data):

    client.post(
        "/auth/register",
        data={
            "worker_id": str(auth_endpoint_data["worker"].id),
            "username": "admin",
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "admin",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["rank_level"] == 1
    assert data["rank_name"] == "Empleado"
    assert "access_token" in data


def test_login_invalid_password(client, auth_endpoint_data):

    client.post(
        "/auth/register",
        data={
            "worker_id": str(auth_endpoint_data["worker"].id),
            "username": "admin",
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "admin",
            "password": "wrong"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Username o contraseña incorrectos"


def test_login_invalid_username(client):

    response = client.post(
        "/auth/login",
        data={
            "username": "ghost",
            "password": "123456"
        }
    )

    assert response.status_code == 401


def test_logout(client):

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Sesión cerrada exitosamente"


def test_me_endpoint(client, leader_user):

    response = client.get("/auth/me")

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "leader"
    assert data["rank_level"] == 2