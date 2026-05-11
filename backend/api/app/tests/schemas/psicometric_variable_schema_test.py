import uuid
import pytest

from app.servicemodels.psicometric_variable_service import PsicometricVariableService

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


def test_get_psicometric_variables(db, psicometric_variable_data):

    service = PsicometricVariableService(db)

    variables = service.get_psicometric_variables()

    assert isinstance(variables, list)
    assert len(variables) >= 1


def test_get_psicometric_variable_by_id(db, psicometric_variable_data):

    service = PsicometricVariableService(db)

    variable = service.get_psicometric_variable(
        psicometric_variable_data.id
    )

    assert variable is not None
    assert variable.name == "Estrés"


def test_get_psicometric_variable_not_found(db):

    service = PsicometricVariableService(db)

    variable = service.get_psicometric_variable(
        uuid.uuid4()
    )

    assert variable is None