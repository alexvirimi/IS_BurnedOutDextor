# app/tests/schemas/group_scheme_test.py

import uuid

from app.schemas.group_scheme import (
    GroupCreate,
    GroupUpdate,
    GroupAssignLeader,
    GroupResponse
)


class TestGroupSchemas:

    def test_group_create_schema(self):

        area_id = uuid.uuid4()
        leader_id = uuid.uuid4()

        payload = GroupCreate(
            name="Backend Team",
            id_area=area_id,
            id_leader=leader_id
        )

        assert payload.name == "Backend Team"
        assert payload.id_area == area_id
        assert payload.id_leader == leader_id

    def test_group_update_schema(self):

        payload = GroupUpdate(
            name="Updated Team"
        )

        assert payload.name == "Updated Team"
        assert payload.id_area is None
        assert payload.id_leader is None

    def test_group_assign_leader_schema(self):

        leader_id = uuid.uuid4()

        payload = GroupAssignLeader(
            id_leader=leader_id
        )

        assert payload.id_leader == leader_id

    def test_group_response_schema(self):

        group_id = uuid.uuid4()
        area_id = uuid.uuid4()
        leader_id = uuid.uuid4()

        response = GroupResponse(
            id=group_id,
            name="Frontend Team",
            id_area=area_id,
            id_leader=leader_id
        )

        assert response.id == group_id
        assert response.name == "Frontend Team"
        assert response.id_area == area_id
        assert response.id_leader == leader_id