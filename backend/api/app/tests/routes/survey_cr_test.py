# app/tests/endpoints/surveys_endpoint_test.py

import uuid
from datetime import date, timedelta

from app.dbmodels.surveys import Surveys


def test_read_surveys(client, db):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta General",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=5),
        status="activa"
    )

    db.add(survey)
    db.commit()

    response = client.get("/survey/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_read_survey_by_id(client, db):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta Backend",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=5),
        status="activa"
    )

    db.add(survey)
    db.commit()

    response = client.get(f"/survey/{survey.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(survey.id)


def test_read_survey_not_found(client):

    response = client.get(f"/survey/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Encuesta no encontrada"


def test_create_survey(client, rrhh_user):

    response = client.post(
        "/survey/",
        data={
            "name": "Nueva Encuesta",
            "aperture_date": str(date.today()),
            "finishing_date": str(date.today() + timedelta(days=10)),
            "status": "activa"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Nueva Encuesta"


def test_update_survey(client, db, rrhh_user):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta Vieja",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=5),
        status="activa"
    )

    db.add(survey)
    db.commit()

    response = client.patch(
        f"/survey/{survey.id}",
        json={
            "name": "Encuesta Actualizada",
            "status": "finalizada"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Encuesta Actualizada"
    assert data["status"] == "finalizada"


def test_update_survey_not_found(client, rrhh_user):

    response = client.patch(
        f"/survey/{uuid.uuid4()}",
        json={
            "name": "No existe"
        }
    )

    assert response.status_code == 404


def test_read_survey_complete(client, db):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta Completa",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=5),
        status="activa"
    )

    db.add(survey)
    db.commit()

    response = client.get(f"/survey/{survey.id}/complete")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Encuesta Completa"
    assert "answer_options" in data