import pytest
from unittest.mock import MagicMock
from uuid import UUID, uuid4
from app.servicemodels.psicometric_variable_service import PsicometricVariableService
from app.dbmodels import PsicometricVariable

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def psicometric_variable_service(mock_db_session):
    return PsicometricVariableService(mock_db_session)

@pytest.fixture
def mock_psicometric_variables():
    return [
        PsicometricVariable(id=uuid4(), name="agotamiento"),
        PsicometricVariable(id=uuid4(), name="despersonalización"),
        PsicometricVariable(id=uuid4(), name="eficacia"),
    ]

def test_get_psicometric_variables(psicometric_variable_service, mock_db_session, mock_psicometric_variables):
    mock_db_session.query.return_value.all.return_value = mock_psicometric_variables
    
    variables = psicometric_variable_service.get_psicometric_variables()
    
    assert len(variables) == 3
    assert variables[0].name == "agotamiento"
    assert variables[1].name == "despersonalización"
    assert variables[2].name == "eficacia"
    mock_db_session.query.assert_called_once_with(PsicometricVariable)

