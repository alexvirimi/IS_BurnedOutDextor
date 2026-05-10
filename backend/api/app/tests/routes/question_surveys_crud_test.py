# app/tests/routes/question_surveys_crud_test.py
import uuid
from datetime import date

from app.dbmodels.question_surveys import QuestionSurveys
from app.dbmodels.questions import Question
from app.dbmodels.surveys import Surveys
from app.dbmodels.psicometric_variable import PsicometricVariable


class TestQuestionSurveyEndpoints:

    def _make_psicometric(self, db, name="burnout"):
        p = PsicometricVariable(id=uuid.uuid4(), name=name)
        db.add(p)
        db.flush()
        return p

    def _make_survey(self, db, name="Encuesta"):
        s = Surveys(
            id=uuid.uuid4(), name=name,
            aperture_date=date.today(), finishing_date=date.today(), status="active"
        )
        db.add(s)
        db.flush()
        return s

    def _make_question(self, db, psicometric_id, text="¿Pregunta?"):
        q = Question(id=uuid.uuid4(), text=text, psicometric_variable_id=psicometric_id)
        db.add(q)
        db.flush()
        return q

    def test_get_question_surveys_success(self, client, db):
        p = self._make_psicometric(db)
        survey = self._make_survey(db, "Encuesta Burnout")
        question = self._make_question(db, p.id, "¿Te sientes cansado?")

        relation = QuestionSurveys(id=uuid.uuid4(), id_survey=survey.id, id_question=question.id)
        db.add(relation)
        db.commit()

        response = client.get("/question_survey/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_question_survey_by_id_success(self, client, db):
        p = self._make_psicometric(db, "general")
        survey = self._make_survey(db, "Encuesta QA")
        question = self._make_question(db, p.id)

        relation = QuestionSurveys(id=uuid.uuid4(), id_survey=survey.id, id_question=question.id)
        db.add(relation)
        db.commit()

        response = client.get(f"/question_survey/{relation.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(relation.id)

    def test_get_question_survey_not_found(self, client):
        response = client.get(f"/question_survey/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Pregunta no encontrada"

    def test_create_question_survey_success(self, client, db):
        p = self._make_psicometric(db, "stress")
        survey = self._make_survey(db)
        question = self._make_question(db, p.id, "¿Nueva pregunta?")

        response = client.post(
            "/question_survey/",
            data={"id_survey": str(survey.id), "id_question": str(question.id)}
        )
        assert response.status_code == 201
        assert response.json()["id_survey"] == str(survey.id)

    def test_update_question_survey_success(self, client, db):
        p = self._make_psicometric(db, "stress2")
        survey1 = self._make_survey(db, "Encuesta 1")
        survey2 = self._make_survey(db, "Encuesta 2")
        question = self._make_question(db, p.id, "Pregunta")

        relation = QuestionSurveys(id=uuid.uuid4(), id_survey=survey1.id, id_question=question.id)
        db.add(relation)
        db.commit()

        response = client.put(
            f"/question_survey/{relation.id}",
            data={"id_survey": str(survey2.id)}
        )
        assert response.status_code == 200
        assert response.json()["id_survey"] == str(survey2.id)

    def test_delete_question_survey_success(self, client, db, rrhh_user):
        p = self._make_psicometric(db, "stress3")
        survey = self._make_survey(db, "Encuesta Delete")
        question = self._make_question(db, p.id, "Eliminar")

        relation = QuestionSurveys(id=uuid.uuid4(), id_survey=survey.id, id_question=question.id)
        db.add(relation)
        db.commit()

        response = client.delete(f"/question_survey/{relation.id}")
        assert response.status_code == 204
