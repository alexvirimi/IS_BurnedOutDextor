#Fail
import uuid
from app.dbmodels import Worker, Group, Rank, Area

class TestWorkerEndpoints:

    def test_get_workers_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="Empleado",
            level=1
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
            name="Mario",
            last_names="Julio",
            age=20,
            gender="M",
            flag=False,
            id_group=group.id,
            id_rank=rank.id
        )

        db.add(rank)
        db.add(area)
        db.commit()

        db.add(group)
        db.commit()

        db.add(worker)
        db.commit()

        response = client.get("/worker/")

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_worker_by_id_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="Empleado",
            level=1
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
            name="Ana",
            last_names="Meza",
            age=22,
            gender="F",
            flag=False,
            id_group=group.id,
            id_rank=rank.id
        )

        db.add(rank)
        db.add(area)
        db.commit()

        db.add(group)
        db.commit()

        db.add(worker)
        db.commit()

        response = client.get(f"/worker/{worker.id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Ana"

    def test_get_worker_not_found(self, client):

        response = client.get(f"/worker/{uuid.uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Trabajador no encontrado"

    def test_create_worker_success(self, client, db, rrhh_user):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="Empleado",
            level=1
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

        db.add(rank)
        db.add(area)
        db.commit()

        db.add(group)
        db.commit()

        response = client.post(
            "/worker/",
            data={
                "name": "Carlos",
                "last_names": "Perez",
                "age": 30,
                "gender": "M",
                "id_group": str(group.id),
                "id_rank": str(rank.id)
            }
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Carlos"

    def test_create_worker_unauthorized(self, client):

        response = client.post(
            "/worker/",
            data={
                "name": "Carlos",
                "last_names": "Perez",
                "age": 30,
                "gender": "M",
                "id_group": str(uuid.uuid4()),
                "id_rank": str(uuid.uuid4())
            }
        )

        assert response.status_code == 401

    
        

    def test_update_worker_flag_rrhh_forbidden(self, client, db, rrhh_user):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="Empleado",
            level=1
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
            name="Pedro",
            last_names="Lopez",
            age=26,
            gender="M",
            flag=False,
            id_group=group.id,
            id_rank=rank.id
        )

        db.add(rank)
        db.add(area)
        db.commit()

        db.add(group)
        db.commit()

        db.add(worker)
        db.commit()

        response = client.patch(
            f"/worker/{worker.id}/flag",
            json={
                "flag": True
            }
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "El personal de RRHH no puede modificar el flag de trabajadores"