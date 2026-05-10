# app/tests/routes/survey_patch_test.py
# Tests for PATCH /survey/{survey_id}

import uuid
from datetime import date, timedelta

from app.dbmodels import Surveys


class TestSurveyPatch:

    # ── helper ─────────────────────────────────────────────────────────────────

    def _make_survey(
        self,
        db,
        *,
        name="Encuesta Original",
        aperture_date=None,
        finishing_date=None,
        status="Activo",
    ) -> Surveys:
        today = date.today()
        survey = Surveys(
            id=uuid.uuid4(),
            name=name,
            aperture_date=aperture_date or today,
            finishing_date=finishing_date or today + timedelta(days=7),
            status=status,
        )
        db.add(survey)
        db.commit()
        return survey

    # ── success: individual fields ─────────────────────────────────────────────

    def test_patch_name_only(self, client, db, rrhh_user):
        """Debe actualizar solo el nombre sin tocar el resto."""
        survey = self._make_survey(db)

        response = client.patch(
            f"/survey/{survey.id}",
            json={"name": "Nombre Actualizado"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nombre Actualizado"
        assert data["status"] == survey.status
        assert data["aperture_date"] == str(survey.aperture_date)
        assert data["finishing_date"] == str(survey.finishing_date)

    def test_patch_status_to_inactivo(self, client, db, rrhh_user):
        """Debe cambiar el estado a Inactivo."""
        survey = self._make_survey(db, status="Activo")

        response = client.patch(
            f"/survey/{survey.id}",
            json={"status": "Inactivo"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "Inactivo"

    def test_patch_status_to_activo(self, client, db, rrhh_user):
        """Debe cambiar el estado a Activo."""
        survey = self._make_survey(db, status="Inactivo")

        response = client.patch(
            f"/survey/{survey.id}",
            json={"status": "Activo"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "Activo"

    def test_patch_aperture_date_only(self, client, db, rrhh_user):
        """Debe actualizar solo la fecha de apertura."""
        survey = self._make_survey(db)
        new_date = str(date.today() + timedelta(days=1))

        response = client.patch(
            f"/survey/{survey.id}",
            json={"aperture_date": new_date},
        )

        assert response.status_code == 200
        assert response.json()["aperture_date"] == new_date

    def test_patch_finishing_date_only(self, client, db, rrhh_user):
        """Debe actualizar solo la fecha de cierre."""
        survey = self._make_survey(db)
        new_date = str(date.today() + timedelta(days=30))

        response = client.patch(
            f"/survey/{survey.id}",
            json={"finishing_date": new_date},
        )

        assert response.status_code == 200
        assert response.json()["finishing_date"] == new_date

    def test_patch_multiple_fields(self, client, db, rrhh_user):
        """Debe actualizar varios campos a la vez."""
        survey = self._make_survey(db)
        today = date.today()

        response = client.patch(
            f"/survey/{survey.id}",
            json={
                "name": "Encuesta Modificada",
                "status": "Inactivo",
                "aperture_date": str(today),
                "finishing_date": str(today + timedelta(days=14)),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Encuesta Modificada"
        assert data["status"] == "Inactivo"
        assert data["aperture_date"] == str(today)
        assert data["finishing_date"] == str(today + timedelta(days=14))

    def test_patch_idempotent_same_values(self, client, db, rrhh_user):
        """Enviar los mismos valores debe ser idempotente."""
        survey = self._make_survey(db, name="Sin Cambio", status="Activo")

        response = client.patch(
            f"/survey/{survey.id}",
            json={"name": "Sin Cambio", "status": "Activo"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Sin Cambio"
        assert data["status"] == "Activo"

    def test_patch_untouched_fields_remain(self, client, db, rrhh_user):
        """Los campos no enviados no deben cambiar."""
        today = date.today()
        survey = self._make_survey(
            db,
            name="Intacta",
            aperture_date=today,
            finishing_date=today + timedelta(days=5),
            status="Activo",
        )

        client.patch(f"/survey/{survey.id}", json={"name": "Solo Nombre"})

        get_resp = client.get(f"/survey/{survey.id}")
        data = get_resp.json()
        assert data["name"] == "Solo Nombre"
        assert data["status"] == "Activo"
        assert data["aperture_date"] == str(today)
        assert data["finishing_date"] == str(today + timedelta(days=5))

    # ── validation errors ──────────────────────────────────────────────────────

    def test_patch_empty_body_rejected(self, client, db, rrhh_user):
        """Un body vacío debe ser rechazado (se requiere al menos un campo)."""
        survey = self._make_survey(db)

        response = client.patch(f"/survey/{survey.id}", json={})

        assert response.status_code == 422

    def test_patch_empty_name_rejected(self, client, db, rrhh_user):
        """Un nombre vacío debe ser rechazado."""
        survey = self._make_survey(db)

        response = client.patch(f"/survey/{survey.id}", json={"name": ""})

        assert response.status_code == 422

    def test_patch_invalid_status_rejected(self, client, db, rrhh_user):
        """Un estado que no sea 'Activo' o 'Inactivo' debe ser rechazado."""
        survey = self._make_survey(db)

        response = client.patch(
            f"/survey/{survey.id}", json={"status": "Borrado"}
        )

        assert response.status_code == 422

    def test_patch_status_wrong_case_rejected(self, client, db, rrhh_user):
        """El status es case-sensitive: 'activo' no es válido."""
        survey = self._make_survey(db)

        response = client.patch(
            f"/survey/{survey.id}", json={"status": "activo"}
        )

        assert response.status_code == 422

    def test_patch_finishing_before_aperture_rejected(self, client, db, rrhh_user):
        """La fecha de cierre no puede ser anterior a la de apertura."""
        today = date.today()
        survey = self._make_survey(db)

        response = client.patch(
            f"/survey/{survey.id}",
            json={
                "aperture_date": str(today + timedelta(days=5)),
                "finishing_date": str(today),
            },
        )

        assert response.status_code == 422

    def test_patch_invalid_date_format(self, client, db, rrhh_user):
        """Una fecha con formato incorrecto debe ser rechazada."""
        survey = self._make_survey(db)

        response = client.patch(
            f"/survey/{survey.id}", json={"aperture_date": "32-13-2026"}
        )

        assert response.status_code == 422

    # ── not found / bad uuid ───────────────────────────────────────────────────

    def test_patch_survey_not_found(self, client, rrhh_user):
        """Debe retornar 404 si la encuesta no existe."""
        response = client.patch(
            f"/survey/{uuid.uuid4()}",
            json={"name": "No existe"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Encuesta no encontrada"

    def test_patch_invalid_uuid(self, client, rrhh_user):
        """Debe retornar 422 si el survey_id no es un UUID válido."""
        response = client.patch(
            "/survey/not-a-uuid",
            json={"name": "Cualquier cosa"},
        )

        assert response.status_code == 422

    # ── auth ───────────────────────────────────────────────────────────────────

    def test_patch_unauthorized_no_session(self, client, db):
        """Debe retornar 401 sin sesión activa."""
        survey = self._make_survey(db)

        response = client.patch(
            f"/survey/{survey.id}", json={"name": "Intento"}
        )

        assert response.status_code == 401

    def test_patch_forbidden_leader(self, client, db, leader_user):
        """Debe retornar 403 si el usuario es líder (nivel 2), no RRHH."""
        survey = self._make_survey(db)

        response = client.patch(
            f"/survey/{survey.id}", json={"name": "Intento líder"}
        )

        assert response.status_code == 403
