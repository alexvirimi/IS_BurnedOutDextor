#Pass
import uuid
from datetime import date

from app.dbmodels import Surveys
from app.schemas.auth_scheme import CurrentUserData


class TestSurveyEndpoints:

    def test_get_surveys_success(self, client, db):

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta Burnout",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="Activa"
        )

        db.add(survey)
        db.commit()

        response = client.get("/survey/")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Encuesta Burnout"

    def test_get_survey_by_id_success(self, client, db):

        survey = Surveys(
            id=uuid.uuid4(),
            name="Encuesta Estrés",
            aperture_date=date.today(),
            finishing_date=date.today(),
            status="Activa"
        )

        db.add(survey)
        db.commit()

        response = client.get(f"/survey/{survey.id}")

        assert response.status_code == 200
        assert response.json()["id"] == str(survey.id)

    def test_get_survey_not_found(self, client):

        response = client.get(f"/survey/{uuid.uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Encuesta no encontrada"

    def test_create_survey_success(self, client, rrhh_user):

        response = client.post(
            "/survey/",
            data={
                "name": "Encuesta General",
                "aperture_date": "2026-01-01",
                "finishing_date": "2026-01-30",
                "status": "Activa"
            }
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Encuesta General"

    def test_create_survey_unauthorized(self, client):

        response = client.post(
            "/survey/",
            data={
                "name": "Encuesta General",
                "aperture_date": "2026-01-01",
                "finishing_date": "2026-01-30",
                "status": "Activa"
            }
        )

        assert response.status_code == 401