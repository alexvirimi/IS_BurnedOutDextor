
import uuid
from datetime import date

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.company import Company


class TestCompanyEndpoints:

    def test_get_workers_info_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="comun",
            level=1
        )

        area = Area(
            id=uuid.uuid4(),
            name="Tecnología"
        )

        group = Group(
            id=uuid.uuid4(),
            name="Backend Team",
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
            
        )

        company = Company(
            id=uuid.uuid4(),
            id_worker=worker.id,
            assigned_tasks=15,
            completed_tasks=12,
            absences=1,
            employee_calls=4,
            worker_type="Remoto",
            location="Medellín",
            start_date=date.today()
        )

        db.add_all([rank, area, group, worker, company])
        db.commit()

        response = client.get("/company/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["worker_type"] == "Remoto"
        assert data[0]["location"] == "Medellín"

    def test_get_worker_info_by_id_success(self, client, db):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="lider",
            level=2
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
            
        )

        company = Company(
            id=uuid.uuid4(),
            id_worker=worker.id,
            assigned_tasks=30,
            completed_tasks=28,
            absences=0,
            employee_calls=2,
            worker_type="Presencial",
            location="Bogotá",
            start_date=date.today()
        )

        db.add_all([rank, area, group, worker, company])
        db.commit()

        response = client.get(f"/company/{company.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(company.id)
        assert data["worker_type"] == "Presencial"
        assert data["location"] == "Bogotá"

    def test_get_worker_info_not_found(self, client):

        fake_id = uuid.uuid4()

        response = client.get(f"/company/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Detalles de trabajador no encontrados"