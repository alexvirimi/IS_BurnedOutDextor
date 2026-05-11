# app/tests/services/surveys_service_test.py

import uuid
from datetime import date, timedelta

from app.servicemodels.surveys_service import SurveyService

from app.dbmodels.surveys import Surveys


def test_create_survey(db):

    service = SurveyService(db)

    payload = {
        "name": "Encuesta Burnout",
        "aperture_date": date.today(),
        "finishing_date": date.today() + timedelta(days=7),
        "status": "activa"
    }

    survey = service.create_survey(payload)

    assert survey is not None
    assert survey.name == "Encuesta Burnout"


def test_get_surveys(db):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta General",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=5),
        status="activa"
    )

    db.add(survey)
    db.commit()

    service = SurveyService(db)

    surveys = service.get_surveys()

    assert len(surveys) >= 1


def test_get_survey_by_id(db):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta TI",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=10),
        status="activa"
    )

    db.add(survey)
    db.commit()

    service = SurveyService(db)

    found = service.get_survey(survey.id)

    assert found is not None
    assert found.id == survey.id


def test_update_survey(db):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta Vieja",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=5),
        status="activa"
    )

    db.add(survey)
    db.commit()

    service = SurveyService(db)

    updated = service.update_survey(
        survey.id,
        {
            "name": "Encuesta Nueva",
            "status": "finalizada"
        }
    )

    assert updated.name == "Encuesta Nueva"
    assert updated.status == "finalizada"


def test_update_survey_not_found(db):

    service = SurveyService(db)

    updated = service.update_survey(
        uuid.uuid4(),
        {
            "name": "No existe"
        }
    )

    assert updated is None


def test_get_survey_complete_empty(db):

    survey = Surveys(
        id=uuid.uuid4(),
        name="Encuesta Completa",
        aperture_date=date.today(),
        finishing_date=date.today() + timedelta(days=10),
        status="activa"
    )

    db.add(survey)
    db.commit()

    service = SurveyService(db)

    result = service.get_survey_complete(survey.id, db)

    assert result is not None
    assert result["name"] == "Encuesta Completa"
    assert isinstance(result["answer_options"], list)