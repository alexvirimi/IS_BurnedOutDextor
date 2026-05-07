# app/tests/routes/answer_cr_test.py
#Pass
import uuid
from datetime import date

from app.dbmodels.answer import Answer, AnswerEnum
from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.question_surveys import QuestionSurveys
from app.dbmodels.questions import Question
from app.dbmodels.ranks import Rank
from app.dbmodels.surveys import Surveys
from app.dbmodels.workers import Worker


class TestAnswersEndpoints:

    def test_get_answers_success(self, client, db):

        # Rank válido existente en el sistema
        rank = Rank(
            id=uuid.UUID("302e3d66-6935-417d-a066-1aaff3e14bd3"),
            rank_name="comun",
            level=1
        )

        area = Area(
            id=uuid.uuid4(),
            name="Tecnología"
        )

        group = Group(
            id=uuid.uuid4(),
            name="Backend Team",
            id_area=area.id,
            id_leader=None
        )

        worker = Worker(
            id=uuid.uuid4(),
            name="Mario",
            last_names="Julio",
            age=20,
            gender="M",
            id_group=group.id,
            id_rank=rank.id,
            flag=False
        )

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

        db.add_all([rank, area, group, worker, survey, question])
        db.commit()

        question_survey = QuestionSurveys(
            id=uuid.uuid4(),
            id_survey=survey.id,
            id_question=question.id
        )

        db.add(question_survey)
        db.commit()

        answer = Answer(
            id=uuid.uuid4(),
            id_worker=worker.id,
            id_group=group.id,
            id_area=area.id,
            id_question_survey=question_survey.id,
            value=AnswerEnum.SIEMPRE,
            created_at=date.today()
        )

        db.add(answer)
        db.commit()

        response = client.get("/answers/")

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["value"] == AnswerEnum.SIEMPRE

    def test_get_answer_by_id_success(self, client, db):

        rank = Rank(
            id=uuid.UUID("36615516-1912-4229-823d-69900b39248a"),
            rank_name="lider",
            level=2
        )

        area = Area(
            id=uuid.uuid4(),
            name="RRHH"
        )

        group = Group(
            id=uuid.uuid4(),
            name="RRHH Team",
            id_area=area.id,
            id_leader=None
        )

        worker = Worker(
            id=uuid.uuid4(),
            name="Ana",
            last_names="Meza",
            age=25,
            gender="F",
            id_group=group.id,
            id_rank=rank.id,
            flag=False
        )

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta Estrés",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="active"
        )

        question = Question(
            id=uuid.uuid4(),
            text="¿Tienes estrés?",
            psicometric_variable="stress"
        )

        db.add_all([rank, area, group, worker, survey, question])
        db.commit()

        question_survey = QuestionSurveys(
            id=uuid.uuid4(),
            id_survey=survey.id,
            id_question=question.id
        )

        db.add(question_survey)
        db.commit()

        answer = Answer(
            id=uuid.uuid4(),
            id_worker=worker.id,
            id_group=group.id,
            id_area=area.id,
            id_question_survey=question_survey.id,
            value=AnswerEnum.A_VECES,
            created_at=date.today()
        )

        db.add(answer)
        db.commit()

        response = client.get(f"/answers/{answer.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == str(answer.id)
        assert data["value"] == AnswerEnum.A_VECES

    def test_get_answer_not_found(self, client):

        fake_id = uuid.uuid4()

        response = client.get(f"/answers/{fake_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Respuesta no encontrada"