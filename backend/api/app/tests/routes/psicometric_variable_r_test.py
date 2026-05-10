# app/tests/routes/psicometric_variable_r_test.py
import uuid

from app.dbmodels.psicometric_variable import PsicometricVariable


class TestPsicometricVariableEndpoints:

    def test_get_psicometric_variables_success(self, client, db):
        variable = PsicometricVariable(
            id=uuid.uuid4(),
            name="Stress"
        )
        db.add(variable)
        db.commit()

        response = client.get("/psicometric_variable/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert any(v["name"] == "Stress" for v in data)
