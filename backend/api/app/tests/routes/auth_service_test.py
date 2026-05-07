# app/tests/routes/auth_cr_test.py
#pass
import uuid

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.auth_user import AuthUser


class TestAuthEndpoints:

    def test_register_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="rrhh",
            level=3
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
            id_rank=rank.id,
            flag=False
        )

        db.add_all([rank, area, group, worker])
        db.commit()

        response = client.post(
            "/auth/register",
            data={
                "worker_id": str(worker.id),
                "username": "mario",
                "password": "1234"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["worker_id"] == str(worker.id)
        assert data["username"] == "mario"

    def test_register_worker_not_found(self, client):

        response = client.post(
            "/auth/register",
            data={
                "worker_id": str(uuid.uuid4()),
                "username": "fake",
                "password": "1234"
            }
        )

        assert response.status_code == 400

    def test_register_username_exists(self, client, db):

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
            name="HR Team",
            id_area=area.id,
            id_leader=None
        )

        worker = Worker(
            id=uuid.uuid4(),
            name="Ana",
            last_names="Meza",
            age=25,
            gender="F",
            id_group=group.id,
            id_rank=rank.id,
            flag=False
        )

        auth_user = AuthUser(
            id=uuid.uuid4(),
            worker_id=worker.id,
            username="ana",
            password="1234"
        )

        db.add_all([rank, area, group, worker, auth_user])
        db.commit()

        response = client.post(
            "/auth/register",
            data={
                "worker_id": str(worker.id),
                "username": "ana",
                "password": "nueva"
            }
        )

        assert response.status_code == 409

    def test_login_success(self, client, db):

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
            name="Dev Team",
            id_area=area.id,
            id_leader=None
        )

        worker = Worker(
            id=uuid.uuid4(),
            name="Luis",
            last_names="Gonzalez",
            age=30,
            gender="M",
            id_group=group.id,
            id_rank=rank.id,
            flag=False
        )

        auth_user = AuthUser(
            id=uuid.uuid4(),
            worker_id=worker.id,
            username="luis",
            password="1234"
        )

        db.add_all([rank, area, group, worker, auth_user])
        db.commit()

        response = client.post(
            "/auth/login",
            data={
                "username": "luis",
                "password": "1234"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["rank_name"] == "lider"
        assert data["rank_level"] == 2

    def test_login_invalid_credentials(self, client):

        response = client.post(
            "/auth/login",
            data={
                "username": "fake",
                "password": "wrong"
            }
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Username o contraseña incorrectos"