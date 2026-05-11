# app/tests/endpoints/survey_assignment_endpoint_test.py

import uuid
from datetime import date

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.surveys import Surveys
from app.dbmodels.survey_assignments import SurveyWorkerAssignment


def create_dependencies(db):

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
        age=22,
        gender="M",
        id_group=group.id,
        id_rank=rank.id
    )

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta",
        aperture_date=date.today(),
        finishing_date=date.today(),
        status="Activa"
    )

    db.add_all([rank, area, group, worker, survey])
    db.commit()

    return worker, survey


def test_assign_survey(client, db, rrhh_user):

    worker, survey = create_dependencies(db)

    response = client.post(
        "/survey-assignment/assign",
        json={
            "id_survey": str(survey.id),
            "worker_ids": [str(worker.id)]
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert len(data) == 1


def test_get_my_surveys(client, db, leader_user):

    worker, survey = create_dependencies(db)

    assignment = SurveyWorkerAssignment(
        id=uuid.uuid4(),
        id_survey=survey.id,
        id_worker=leader_user.worker_id
    )

    db.add(assignment)
    db.commit()

    response = client.get("/survey-assignment/my-surveys")

    assert response.status_code == 200


def test_get_survey_assignments(client, db, rrhh_user):

    worker, survey = create_dependencies(db)

    assignment = SurveyWorkerAssignment(
        id=uuid.uuid4(),
        id_survey=survey.id,
        id_worker=worker.id
    )

    db.add(assignment)
    db.commit()

    response = client.get(
        f"/survey-assignment/survey/{survey.id}/assignments"
    )

    assert response.status_code == 200


