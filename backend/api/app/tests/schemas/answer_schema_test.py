import uuid
import pytest

from datetime import date
from fastapi import HTTPException

from app.servicemodels.answer_service import AnswerService

from app.dbmodels.answer import AnswerEnum
from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.questions import Question
from app.dbmodels.surveys import Surveys
from app.dbmodels.question_surveys import QuestionSurveys
from app.dbmodels.psicometric_variable import PsicometricVariable


@pytest.fixture
def answer_data(db):

    rank = Rank(
        id=uuid.uuid4(),
        rank_name="Empleado",
        level=1
    )

    area = Area(
        id=uuid.uuid4(),
        name="Tecnología"
    )

    group = Group(
        id=uuid.uuid4(),
        name="Backend",
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
        id_rank=rank.id
    )

    psicometric_variable = PsicometricVariable(
        id=uuid.uuid4(),
        name="Estrés"
    )

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta Burnout",
        aperture_date=date(2025, 1, 1),
        finishing_date=date(2025, 12, 31),
        status="ACTIVA"
    )

    question = Question(
        id=uuid.uuid4(),
        text="¿Cómo te sientes?",
        psicometric_variable_id=psicometric_variable.id
    )

    question_survey = QuestionSurveys(
        id=uuid.uuid4(),
        id_survey=survey.id,
        id_question=question.id
    )

    db.add_all([
        rank,
        area,
        group,
        worker,
        psicometric_variable,
        survey,
        question,
        question_survey
    ])

    db.commit()

    return {
        "worker": worker,
        "group": group,
        "area": area,
        "survey": survey,
        "question": question,
        "question_survey": question_survey
    }


def test_get_answers(db):

    service = AnswerService(db)

    answers = service.get_answers()

    assert isinstance(answers, list)


def test_create_answer(db, answer_data):

    service = AnswerService(db)

    payload = {
        "id_worker": answer_data["worker"].id,
        "id_group": answer_data["group"].id,
        "id_area": answer_data["area"].id,
        "id_question_survey": answer_data["question_survey"].id,
        "value": AnswerEnum.SIEMPRE,
        "created_at": date.today()
    }

    created = service.create_answer(payload)

    assert created.id is not None
    assert created.value == AnswerEnum.SIEMPRE


def test_create_answer_invalid_worker(db, answer_data):

    service = AnswerService(db)

    payload = {
        "id_worker": uuid.uuid4(),
        "id_group": answer_data["group"].id,
        "id_area": answer_data["area"].id,
        "id_question_survey": answer_data["question_survey"].id,
        "value": AnswerEnum.A_VECES,
        "created_at": date.today()
    }

    with pytest.raises(HTTPException) as exc:

        service.create_answer(payload)

    assert exc.value.status_code == 404
    assert exc.value.detail == "El trabajador no existe"


def test_get_answer_by_id(db, answer_data):

    service = AnswerService(db)

    payload = {
        "id_worker": answer_data["worker"].id,
        "id_group": answer_data["group"].id,
        "id_area": answer_data["area"].id,
        "id_question_survey": answer_data["question_survey"].id,
        "value": AnswerEnum.CASI_SIEMPRE,
        "created_at": date.today()
    }

    created = service.create_answer(payload)

    found = service.get_answer_by_id(created.id)

    assert found is not None
    assert found.id == created.id


def test_create_answer_from_user(db, answer_data):

    service = AnswerService(db)

    created = service.create_answer_from_user(
        worker_id=answer_data["worker"].id,
        question_survey_id=answer_data["question_survey"].id,
        value=AnswerEnum.NUNCA
    )

    assert created.id is not None
    assert created.id_worker == answer_data["worker"].id


def test_get_answers_by_worker(db, answer_data):

    service = AnswerService(db)

    service.create_answer_from_user(
        worker_id=answer_data["worker"].id,
        question_survey_id=answer_data["question_survey"].id,
        value=AnswerEnum.A_VECES
    )

    answers = service.get_answers_by_worker(
        answer_data["worker"].id
    )

    assert len(answers) >= 1
    assert answers[0].id_worker == answer_data["worker"].id


