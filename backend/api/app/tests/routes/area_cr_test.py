from uuid import uuid4

from app.dbmodels.area import Area


class TestAreasEndpoints:

    def test_get_areas_success(self, client, db):

        area1 = Area(
            id=uuid4(),
            name="Tecnología"
        )

        area2 = Area(
            id=uuid4(),
            name="RRHH"
        )

        db.add_all([area1, area2])
        db.commit()

        response = client.get("/areas/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2

    def test_get_area_by_id_success(self, client, db):

        area = Area(
            id=uuid4(),
            name="Marketing"
        )

        db.add(area)
        db.commit()

        response = client.get(f"/areas/{area.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "Marketing"

    def test_get_area_not_found(self, client):

        response = client.get(f"/areas/{uuid4()}")

        assert response.status_code == 404