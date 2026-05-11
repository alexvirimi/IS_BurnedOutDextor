import uuid
import pytest

from datetime import date

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
def endpoint_data(db):

    rank = Rank(
        id=uuid.uuid4(),
        rank_name="Empleado",
        level=1
    )

    area = Area(
        id=uuid.uuid4(),
        name="TI"
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
        text="¿Pregunta?",
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
        "question_survey": question_survey
    }


def test_read_answers(client):

    response = client.get("/answers/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_answer_rrhh(client, rrhh_user, endpoint_data):

    response = client.post(
        "/answers/",
        data={
            "id_worker": str(endpoint_data["worker"].id),
            "id_group": str(endpoint_data["group"].id),
            "id_area": str(endpoint_data["area"].id),
            "id_question_survey": str(endpoint_data["question_survey"].id),
            "value": AnswerEnum.SIEMPRE
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id_worker"] == str(endpoint_data["worker"].id)
    assert data["value"] == AnswerEnum.SIEMPRE


def test_create_answer_without_rrhh(client, leader_user, endpoint_data):

    response = client.post(
        "/answers/",
        data={
            "id_worker": str(endpoint_data["worker"].id),
            "id_group": str(endpoint_data["group"].id),
            "id_area": str(endpoint_data["area"].id),
            "id_question_survey": str(endpoint_data["question_survey"].id),
            "value": AnswerEnum.A_VECES
        }
    )

    assert response.status_code == 403


def test_respond_to_question(client, leader_user, endpoint_data):

    response = client.post(
        "/answers/respond",
        data={
            "id_question_survey": str(endpoint_data["question_survey"].id),
            "value": AnswerEnum.CASI_SIEMPRE
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["value"] == AnswerEnum.CASI_SIEMPRE


def test_read_answer_by_id(client, rrhh_user, endpoint_data):

    create_response = client.post(
        "/answers/",
        data={
            "id_worker": str(endpoint_data["worker"].id),
            "id_group": str(endpoint_data["group"].id),
            "id_area": str(endpoint_data["area"].id),
            "id_question_survey": str(endpoint_data["question_survey"].id),
            "value": AnswerEnum.SIEMPRE
        }
    )

    answer_id = create_response.json()["id"]

    response = client.get(f"/answers/{answer_id}")

    assert response.status_code == 200
    assert response.json()["id"] == answer_id


def test_read_answer_not_found(client):

    response = client.get(f"/answers/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Respuesta no encontrada"


def test_read_my_answers(client, leader_user):

    response = client.get("/answers/my/all")

    assert response.status_code == 200
    assert isinstance(response.json(), list)