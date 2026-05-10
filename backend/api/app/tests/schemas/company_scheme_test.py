# app/tests/schemas/company_scheme_test.py

import uuid
from datetime import date

from app.schemas.company_scheme import (
    CompanyCreate,
    CompanyResponse
)


class TestCompanySchemas:

    def test_company_create_schema(self):

        worker_id = uuid.uuid4()

        payload = CompanyCreate(
            id_worker=worker_id,
            assigned_tasks=15,
            completed_tasks=10,
            absences=2,
            employee_calls=5,
            worker_type="Remoto",
            location="Medellín",
            start_date=date.today()
        )

        assert payload.id_worker == worker_id
        assert payload.assigned_tasks == 15
        assert payload.completed_tasks == 10
        assert payload.absences == 2
        assert payload.employee_calls == 5
        assert payload.worker_type == "Remoto"
        assert payload.location == "Medellín"

    def test_company_response_schema(self):

        company_id = uuid.uuid4()
        worker_id = uuid.uuid4()

        response = CompanyResponse(
            id=company_id,
            id_worker=worker_id,
            assigned_tasks=20,
            completed_tasks=18,
            absences=1,
            employee_calls=3,
            worker_type="Híbrido",
            location="Bogotá",
            start_date=date.today()
        )

        assert response.id == company_id
        assert response.id_worker == worker_id
        assert response.assigned_tasks == 20
        assert response.completed_tasks == 18
        assert response.worker_type == "Híbrido"
        assert response.location == "Bogotá"