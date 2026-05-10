from app.schemas.rank_scheme import RankCreate, RankResponse
from uuid import uuid4


class TestRankSchemas:

    def test_rank_create_schema(self):

        schema = RankCreate(
            rank_name="rrhh",
            level=3
        )

        assert schema.rank_name == "rrhh"
        assert schema.level == 3

    def test_rank_response_schema(self):

        rank_id = uuid4()

        schema = RankResponse(
            id=rank_id,
            rank_name="lider",
            level=2
        )

        assert schema.id == rank_id
        assert schema.rank_name == "lider"
        assert schema.level == 2