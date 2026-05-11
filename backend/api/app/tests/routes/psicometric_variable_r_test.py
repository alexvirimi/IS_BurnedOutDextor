import uuid
import pytest

from app.dbmodels.psicometric_variable import PsicometricVariable


@pytest.fixture
def psicometric_variable_data(db):

    variable = PsicometricVariable(
        id=uuid.uuid4(),
        name="Estrés"
    )

    db.add(variable)
    db.commit()

    return variable


def test_read_psicometric_variables(
    client,
    psicometric_variable_data
):
    response = client.get("/psicometric_variable/")
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    assert data[0]["name"] == "Estrés"