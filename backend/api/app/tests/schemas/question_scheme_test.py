# app/tests/schemas/questions_scheme_test.py

import uuid
from app.schemas.questions_scheme import QuestionCreate, QuestionUpdate


class TestQuestionSchemas:

    def test_question_create_schema(self):
        psicometric_id = uuid.uuid4()

        schema = QuestionCreate(
            text="¿Te sientes cansado?",
            psicometric_variable_id=psicometric_id
        )

        assert schema.text == "¿Te sientes cansado?"
        assert schema.psicometric_variable_id == psicometric_id

    def test_question_update_schema(self):
        schema = QuestionUpdate(
            text="Nueva pregunta"
        )

        assert schema.text == "Nueva pregunta"
        assert schema.psicometric_variable_id is None
