# app/tests/routes/question_cr_test.py
#fail
import uuid

from app.dbmodels.questions import Question


class TestQuestionEndpoints:

    def test_get_questions_success(self, client, db):

        question = Question(
            id=uuid.uuid4(),
            text="¿Te sientes estresado?",
            psicometric_variable="stress"
        )

        db.add(question)
        db.commit()

        response = client.get("/question/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["text"] == "¿Te sientes estresado?"

    def test_get_question_by_id_success(self, client, db):

        question = Question(
            id=uuid.uuid4(),
            text="¿Te gusta tu trabajo?",
            psicometric_variable="satisfaction"
        )

        db.add(question)
        db.commit()

        response = client.get(f"/question/{question.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(question.id)
        assert data["text"] == question.text

    def test_get_question_not_found(self, client):

        fake_id = uuid.uuid4()

        response = client.get(f"/question/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Pregunta no encontrada"

    def test_create_question_success(self, client, rrhh_user):

        response = client.post(
            "/question/",
            data={
                "text": "¿Te sientes motivado?",
                "psicometric_variable": "motivation"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["text"] == "¿Te sientes motivado?"
        assert data["psicometric_variable"] == "motivation"

    def test_update_question_success(self, client, db, rrhh_user):

        question = Question(
            id=uuid.uuid4(),
            text="Pregunta vieja",
            psicometric_variable="stress"
        )

        db.add(question)
        db.commit()

        response = client.put(
            f"/question/{question.id}",
            data={
                "text": "Pregunta nueva"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["text"] == "Pregunta nueva"

    def test_update_question_not_found(self, client, rrhh_user):

        fake_id = uuid.uuid4()

        response = client.put(
            f"/question/{fake_id}",
            data={
                "text": "Nueva"
            }
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Pregunta no encontrada"

    def test_delete_question_success(self, client, db, rrhh_user):

        question = Question(
            id=uuid.uuid4(),
            text="Pregunta a eliminar",
            psicometric_variable="stress"
        )

        db.add(question)
        db.commit()

        response = client.delete(f"/question/{question.id}")

        assert response.status_code == 204

    def test_delete_question_not_found(self, client, rrhh_user):

        fake_id = uuid.uuid4()

        response = client.delete(f"/question/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Pregunta no encontrada"