# app/tests/schemas/question_surveys_scheme_test.py

import uuid

from app.schemas.question_surveys_scheme import (
    QuestionSurveyCreate,
    QuestionSurveyUpdate,
    AssignQuestions
)


class TestQuestionSurveySchemas:

    def test_question_survey_create_schema(self):

        survey_id = uuid.uuid4()
        question_id = uuid.uuid4()

        schema = QuestionSurveyCreate(
            id_survey=survey_id,
            id_question=question_id
        )

        assert schema.id_survey == survey_id
        assert schema.id_question == question_id

    def test_question_survey_update_schema(self):

        survey_id = uuid.uuid4()

        schema = QuestionSurveyUpdate(
            id_survey=survey_id
        )

        assert schema.id_survey == survey_id
        assert schema.id_question is None

    def test_assign_questions_schema(self):

        survey_id = uuid.uuid4()
        question_ids = [uuid.uuid4(), uuid.uuid4()]

        schema = AssignQuestions(
            id_survey=survey_id,
            question_ids=question_ids
        )

        assert schema.id_survey == survey_id
        assert len(schema.question_ids) == 2