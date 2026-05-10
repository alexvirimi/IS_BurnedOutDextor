# app/tests/schemas/auth_scheme_test.py
import uuid
from app.schemas.auth_scheme import (
    AuthUserCreate,
    AuthUserResponse,
    LoginRequest,
    LoginResponse,
    CurrentUserData
)


class TestAuthSchemas:

    def test_auth_user_create_schema(self):
        worker_id = uuid.uuid4()
        payload = AuthUserCreate(worker_id=worker_id, username="mario", password="1234")
        assert payload.worker_id == worker_id
        assert payload.username == "mario"
        assert payload.password == "1234"

    def test_auth_user_response_schema(self):
        auth_id = uuid.uuid4()
        worker_id = uuid.uuid4()
        response = AuthUserResponse(id=auth_id, worker_id=worker_id, username="ana")
        assert response.id == auth_id
        assert response.worker_id == worker_id
        assert response.username == "ana"

    def test_login_request_schema(self):
        payload = LoginRequest(username="julio", password="admin123")
        assert payload.username == "julio"
        assert payload.password == "admin123"

    def test_login_response_schema(self):
        auth_user_id = uuid.uuid4()
        worker_id = uuid.uuid4()
        response = LoginResponse(
            worker_id=worker_id,
            rank_level=3,
            rank_name="rrhh",
            auth_user_id=auth_user_id
        )
        assert response.worker_id == worker_id
        assert response.rank_level == 3
        assert response.rank_name == "rrhh"
        assert response.auth_user_id == auth_user_id

    def test_current_user_data_schema(self):
        auth_user_id = uuid.uuid4()
        worker_id = uuid.uuid4()
        group_id = uuid.uuid4()
        current_user = CurrentUserData(
            auth_user_id=auth_user_id,
            worker_id=worker_id,
            username="mario",
            rank_level=2,
            rank_name="lider",
            id_group=group_id
        )
        assert current_user.username == "mario"
        assert current_user.rank_level == 2
        assert current_user.rank_name == "lider"
        assert current_user.auth_user_id == auth_user_id
