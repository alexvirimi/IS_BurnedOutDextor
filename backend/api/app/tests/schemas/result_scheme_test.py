from datetime import date
from uuid import uuid4

from app.schemas.result_scheme import ResultCreate, ResultResponse


class TestResultSchemas:

    def test_result_create_schema(self):

        schema = ResultCreate(
            id_worker=uuid4(),
            id_group=uuid4(),
            id_area=uuid4(),
            id_survey=uuid4(),
            burnout_score="medium"
        )

        assert schema.burnout_score == "medium"

    def test_result_response_schema(self):

        result_id = uuid4()

        schema = ResultResponse(
            id=result_id,
            id_worker=uuid4(),
            id_group=uuid4(),
            id_area=uuid4(),
            id_survey=uuid4(),
            burnout_score="high",
            generation_date=date.today()
        )

        assert schema.id == result_id
        assert schema.burnout_score == "high"