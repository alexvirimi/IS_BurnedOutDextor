# app/tests/routes/question_surveys_cr_test.py
#fail
import uuid
from datetime import date

from app.dbmodels.question_surveys import QuestionSurveys
from app.dbmodels.questions import Question
from app.dbmodels.surveys import Surveys


class TestQuestionSurveyEndpoints:

    def test_get_question_surveys_success(self, client, db):

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta Burnout",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        question = Question(
            id=uuid.uuid4(),
            text="¿Te sientes cansado?",
            psicometric_variable="burnout"
        )

        db.add_all([survey, question])
        db.commit()

        relation = QuestionSurveys(
            id=uuid.uuid4(),
            id_survey=survey.id,
            id_question=question.id
        )

        db.add(relation)
        db.commit()

        response = client.get("/question_survey/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1

    def test_get_question_survey_by_id_success(self, client, db):

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta QA",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        question = Question(
            id=uuid.uuid4(),
            text="¿Pregunta?",
            psicometric_variable="general"
        )

        db.add_all([survey, question])
        db.commit()

        relation = QuestionSurveys(
            id=uuid.uuid4(),
            id_survey=survey.id,
            id_question=question.id
        )

        db.add(relation)
        db.commit()

        response = client.get(f"/question_survey/{relation.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(relation.id)

    def test_get_question_survey_not_found(self, client):

        fake_id = uuid.uuid4()

        response = client.get(f"/question_survey/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Pregunta no encontrada"

    def test_create_question_survey_success(self, client, db):

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        question = Question(
            id=uuid.uuid4(),
            text="¿Nueva pregunta?",
            psicometric_variable="stress"
        )

        db.add_all([survey, question])
        db.commit()

        response = client.post(
            "/question_survey/",
            data={
                "id_survey": str(survey.id),
                "id_question": str(question.id)
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id_survey"] == str(survey.id)

    def test_update_question_survey_success(self, client, db):

        survey1 = Surveys(
            id=uuid.uuid4(),
            name="Encuesta 1",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        survey2 = Surveys(
            id=uuid.uuid4(),
            name="Encuesta 2",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        question = Question(
            id=uuid.uuid4(),
            text="Pregunta",
            psicometric_variable="stress"
        )

        db.add_all([survey1, survey2, question])
        db.commit()

        relation = QuestionSurveys(
            id=uuid.uuid4(),
            id_survey=survey1.id,
            id_question=question.id
        )

        db.add(relation)
        db.commit()

        response = client.put(
            f"/question_survey/{relation.id}",
            data={
                "id_survey": str(survey2.id)
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id_survey"] == str(survey2.id)

    def test_delete_question_survey_success(self, client, db, rrhh_user):

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta Delete",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        question = Question(
            id=uuid.uuid4(),
            text="Eliminar",
            psicometric_variable="stress"
        )

        db.add_all([survey, question])
        db.commit()

        relation = QuestionSurveys(
            id=uuid.uuid4(),
            id_survey=survey.id,
            id_question=question.id
        )

        db.add(relation)
        db.commit()

        response = client.delete(
            f"/question_survey/{relation.id}"
        )

        assert response.status_code == 204

    def test_assign_questions_success(self, client, db):

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta Multiple",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        question1 = Question(
            id=uuid.uuid4(),
            text="Pregunta 1",
            psicometric_variable="stress"
        )

        question2 = Question(
            id=uuid.uuid4(),
            text="Pregunta 2",
            psicometric_variable="burnout"
        )

        db.add_all([survey, question1, question2])
        db.commit()

        response = client.post(
            "/question_survey/assign",
            data=[
                ("id_survey", str(survey.id)),
                ("question_ids", str(question1.id)),
                ("question_ids", str(question2.id))
            ]
        )

        assert response.status_code == 200