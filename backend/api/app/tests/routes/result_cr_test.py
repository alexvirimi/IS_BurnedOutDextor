# app/tests/endpoints/result_endpoint_test.py

import uuid
from datetime import date

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.surveys import Surveys
from app.dbmodels.result import Result


def create_result_dependencies(db):

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

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta",
        aperture_date=date.today(),
        finishing_date=date.today(),
        status="Activa"
    )

    db.add_all([rank, area, group, worker, survey])
    db.commit()

    return area, group, worker, survey


def test_read_results_rrhh(client, db, rrhh_user):

    response = client.get("/results/")

    assert response.status_code == 200


def test_create_result(client, db, leader_user):

    area, group, worker, survey = create_result_dependencies(db)

    response = client.post(
        "/results/",
        data={
            "id_worker": str(worker.id),
            "id_group": str(group.id),
            "id_area": str(area.id),
            "id_survey": str(survey.id),
            "burnout_score": "Moderado"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["burnout_score"] == "Moderado"


def test_read_result_by_id(client, db, rrhh_user):

    area, group, worker, survey = create_result_dependencies(db)

    result = Result(
        id=uuid.uuid4(),
        id_worker=worker.id,
        id_group=group.id,
        id_area=area.id,
        id_survey=survey.id,
        burnout_score="Alto",
        generation_date=date.today(),
        flag=False
    )

    db.add(result)
    db.commit()

    response = client.get(f"/results/{result.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(result.id)


def test_update_result_flag(client, db, leader_user):

    area, group, worker, survey = create_result_dependencies(db)

    result = Result(
        id=uuid.uuid4(),
        id_worker=worker.id,
        id_group=leader_user.id_group,
        id_area=area.id,
        id_survey=survey.id,
        burnout_score="Crítico",
        generation_date=date.today(),
        flag=False
    )

    db.add(result)
    db.commit()

    response = client.patch(
        f"/results/{result.id}/flag",
        json={
            "flag": True
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["flag"] is True


def test_update_result_flag_rrhh_forbidden(client, db, rrhh_user):

    area, group, worker, survey = create_result_dependencies(db)

    result = Result(
        id=uuid.uuid4(),
        id_worker=worker.id,
        id_group=group.id,
        id_area=area.id,
        id_survey=survey.id,
        burnout_score="Crítico",
        generation_date=date.today(),
        flag=False
    )

    db.add(result)
    db.commit()

    response = client.patch(
        f"/results/{result.id}/flag",
        json={
            "flag": True
        }
    )

    assert response.status_code == 403