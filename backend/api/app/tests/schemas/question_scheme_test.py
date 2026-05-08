# app/tests/schemas/questions_scheme_test.py

from app.schemas.questions_scheme import (
    QuestionCreate,
    QuestionUpdate
)


class TestQuestionSchemas:

    def test_question_create_schema(self):

        schema = QuestionCreate(
            text="¿Te sientes cansado?",
            psicometric_variable="burnout"
        )

        assert schema.text == "¿Te sientes cansado?"
        assert schema.psicometric_variable == "burnout"

    def test_question_update_schema(self):

        schema = QuestionUpdate(
            text="Nueva pregunta"
        )

        assert schema.text == "Nueva pregunta"
        assert schema.psicometric_variable is None