import uuid

from app.dbmodels.psicometric_variable import PsicometricVariable


class TestPsicometricVariableEndpoints:

    def test_get_psicometric_variables_success(self, client, db):

        variable = PsicometricVariable(
            id=uuid.uuid4(),
            name="Stress",
            description="Stress level variable"
        )

        db.add(variable)
        db.commit()

        response = client.get("/psicometric_variable/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) >= 1

        assert data[0]["name"] == "Stress"

    def test_get_psicometric_variable_by_id_success(self, client, db):

        variable = PsicometricVariable(
            id=uuid.uuid4(),
            name="Anxiety",
            description="Anxiety variable"
        )

        db.add(variable)
        db.commit()

        response = client.get(
            f"/psicometric_variable/{variable.id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(variable.id)

        assert data["name"] == "Anxiety"

    def test_get_psicometric_variable_not_found(self, client):

        fake_id = uuid.uuid4()

        response = client.get(
            f"/psicometric_variable/{fake_id}"
        )

        assert response.status_code == 404