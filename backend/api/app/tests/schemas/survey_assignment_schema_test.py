# app/tests/services/survey_assignment_service_test.py

import uuid
from datetime import date

from app.servicemodels.survey_assignment_service import SurveyAssignmentService

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.surveys import Surveys
from app.dbmodels.survey_assignments import SurveyWorkerAssignment


def create_assignment_dependencies(db):

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


def test_assign_survey_to_workers(db):

    worker, survey = create_assignment_dependencies(db)

    service = SurveyAssignmentService(db)

    result = service.assign_survey_to_workers(
        survey.id,
        [worker.id]
    )

    assert len(result) == 1
    assert result[0].id_worker == worker.id


def test_can_worker_respond_survey(db):

    worker, survey = create_assignment_dependencies(db)

    assignment = SurveyWorkerAssignment(
        id=uuid.uuid4(),
        id_survey=survey.id,
        id_worker=worker.id
    )

    db.add(assignment)
    db.commit()

    service = SurveyAssignmentService(db)

    can_respond = service.can_worker_respond_survey(
        worker.id,
        survey.id
    )

    assert can_respond is True


def test_get_my_surveys(db):

    worker, survey = create_assignment_dependencies(db)

    assignment = SurveyWorkerAssignment(
        id=uuid.uuid4(),
        id_survey=survey.id,
        id_worker=worker.id
    )

    db.add(assignment)
    db.commit()

    service = SurveyAssignmentService(db)

    surveys = service.get_my_surveys(worker.id)

    assert len(surveys) == 1
    assert surveys[0]["name"] == survey.name
