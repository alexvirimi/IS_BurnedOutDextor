# app/tests/routes/group_cr_test.py
#pass
import uuid

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker


class TestGroupEndpoints:

    def test_get_groups_success(self, client, db):

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

        db.add_all([area, group])
        db.commit()

        response = client.get("/group/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["name"] == "Backend Team"

    def test_get_group_by_id_success(self, client, db):

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

        db.add_all([area, group])
        db.commit()

        response = client.get(f"/group/{group.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(group.id)
        assert data["name"] == "HR Team"

    def test_get_group_not_found(self, client):

        fake_id = uuid.uuid4()

        response = client.get(f"/group/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Grupo no encontrado"

    def test_assign_leader_success(self, client, db, rrhh_user):

        rank = Rank(
            id=uuid.uuid4(),
            rank_name="lider",
            level=2
        )

        area = Area(
            id=uuid.uuid4(),
            name="Development"
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
            age=28,
            gender="M",
            id_group=group.id,
            id_rank=rank.id,
            
        )

        db.add_all([rank, area, group, worker])
        db.commit()

        response = client.patch(
            f"/group/{group.id}/leader",
            data={
                "id_leader": str(worker.id)
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id_leader"] == str(worker.id)

    def test_assign_leader_group_not_found(self, client, rrhh_user):

        fake_group_id = uuid.uuid4()
        fake_worker_id = uuid.uuid4()

        response = client.patch(
            f"/group/{fake_group_id}/leader",
            data={
                "id_leader": str(fake_worker_id)
            }
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Grupo no encontrado"

    def test_assign_leader_worker_not_found(self, client, db, rrhh_user):

        area = Area(
            id=uuid.uuid4(),
            name="QA"
        )

        group = Group(
            id=uuid.uuid4(),
            name="QA Team",
            id_area=area.id,
            id_leader=None
        )

        db.add(area)
        db.commit()

        db.add(group)
        db.commit()
        response = client.patch(
            f"/group/{group.id}/leader",
            data={
                "id_leader": str(uuid.uuid4())
            }
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Trabajador no encontrado"

    