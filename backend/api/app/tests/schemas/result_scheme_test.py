# app/tests/services/result_service_test.py

import uuid
from datetime import date

import pytest
from fastapi import HTTPException

from app.servicemodels.result_service import ResultService

from app.dbmodels.area import Area
from app.dbmodels.groups import Group
from app.dbmodels.ranks import Rank
from app.dbmodels.workers import Worker
from app.dbmodels.surveys import Surveys
from app.dbmodels.result import Result


@pytest.fixture
def result_data(db):

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
        age=22,
        gender="M",
        id_group=group.id,
        id_rank=rank.id
    )

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta Burnout",
        aperture_date=date.today(),
        finishing_date=date.today(),
        status="Activa"
    )

    db.add_all([rank, area, group, worker, survey])
    db.commit()

    return {
        "rank": rank,
        "area": area,
        "group": group,
        "worker": worker,
        "survey": survey
    }


def test_create_result(db, result_data):

    service = ResultService(db)

    payload = {
        "id_worker": result_data["worker"].id,
        "id_group": result_data["group"].id,
        "id_area": result_data["area"].id,
        "id_survey": result_data["survey"].id,
        "burnout_score": "Moderado",
        "generation_date": date.today()
    }

    result = service.create_result(payload)

    assert result is not None
    assert result.burnout_score == "Moderado"


def test_create_result_invalid_worker(db, result_data):

    service = ResultService(db)

    payload = {
        "id_worker": uuid.uuid4(),
        "id_group": result_data["group"].id,
        "id_area": result_data["area"].id,
        "id_survey": result_data["survey"].id,
        "burnout_score": "Alto",
        "generation_date": date.today()
    }

    with pytest.raises(HTTPException) as exc:
        service.create_result(payload)

    assert exc.value.status_code == 404
    assert exc.value.detail == "El trabajador no existe"


def test_get_result_by_id(db, result_data):

    result = Result(
        id=uuid.uuid4(),
        id_worker=result_data["worker"].id,
        id_group=result_data["group"].id,
        id_area=result_data["area"].id,
        id_survey=result_data["survey"].id,
        burnout_score="Bajo",
        generation_date=date.today(),
        flag=False
    )

    db.add(result)
    db.commit()

    service = ResultService(db)

    found = service.get_result_by_id(result.id)

    assert found is not None
    assert found.id == result.id


def test_get_results_by_worker(db, result_data):

    result = Result(
        id=uuid.uuid4(),
        id_worker=result_data["worker"].id,
        id_group=result_data["group"].id,
        id_area=result_data["area"].id,
        id_survey=result_data["survey"].id,
        burnout_score="Bajo",
        generation_date=date.today(),
        flag=False
    )

    db.add(result)
    db.commit()

    service = ResultService(db)

    results = service.get_results_by_worker(result_data["worker"].id)

    assert len(results) == 1


def test_update_result_flag(db, result_data):

    result = Result(
        id=uuid.uuid4(),
        id_worker=result_data["worker"].id,
        id_group=result_data["group"].id,
        id_area=result_data["area"].id,
        id_survey=result_data["survey"].id,
        burnout_score="Crítico",
        generation_date=date.today(),
        flag=False
    )

    db.add(result)
    db.commit()

    service = ResultService(db)

    updated = service.update_result_flag(result.id, True)

    assert updated.flag is True