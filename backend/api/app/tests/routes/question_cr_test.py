# app/tests/routes/question_cr_test.py
import uuid

from app.dbmodels.questions import Question
from app.dbmodels.psicometric_variable import PsicometricVariable


class TestQuestionEndpoints:

    def test_get_questions_success(self, client, db):
        psicometric = PsicometricVariable(
            id=uuid.uuid4(),
            name="burnout"
        )
        db.add(psicometric)
        db.flush()

        question = Question(
            id=uuid.uuid4(),
            text="¿Te sientes estresado?",
            psicometric_variable_id=psicometric.id
        )
        db.add(question)
        db.commit()

        response = client.get("/question/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "¿Te sientes estresado?"

    def test_get_question_by_id_success(self, client, db):
        psicometric = PsicometricVariable(
            id=uuid.uuid4(),
            name="satisfaction"
        )
        db.add(psicometric)
        db.flush()

        question = Question(
            id=uuid.uuid4(),
            text="¿Te gusta tu trabajo?",
            psicometric_variable_id=psicometric.id
        )
        db.add(question)
        db.commit()

        response = client.get(f"/question/{question.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(question.id)
        assert data["text"] == question.text

    def test_get_question_not_found(self, client):
        response = client.get(f"/question/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Pregunta no encontrada"

    def test_create_question_success(self, client, db, rrhh_user):
        psicometric = PsicometricVariable(
            id=uuid.uuid4(),
            name="motivation"
        )
        db.add(psicometric)
        db.flush()

        response = client.post(
            "/question/",
            data={
                "text": "¿Te sientes motivado?",
                "psicometric_variable_id": str(psicometric.id)
            }
        )
        assert response.status_code == 201

        data = response.json()
        assert data["text"] == "¿Te sientes motivado?"
        assert data["psicometric_variable"]["id"] == str(psicometric.id)
