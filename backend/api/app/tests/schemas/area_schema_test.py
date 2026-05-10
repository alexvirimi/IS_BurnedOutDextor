# Tests para los esquemas de áreas.

import pytest
from uuid import uuid4
from pydantic import ValidationError

from app.schemas.area_scheme import AreaCreate, AreaResponse


class TestAreaCreate:

    def test_create_area_success(self):
        """Debe crear correctamente un AreaCreate válido"""

        area = AreaCreate(
            name="Recursos Humanos"
        )

        assert area.name == "Recursos Humanos"

    def test_create_area_empty_name(self):
        """Debe permitir string vacío si no hay validaciones"""

        area = AreaCreate(
            name=""
        )

        assert area.name == ""

    def test_create_area_invalid_type(self):
        """Debe fallar si el tipo de name es inválido"""

        with pytest.raises(ValidationError):

            AreaCreate(
                name=123
            )

    def test_as_form_method(self):
        """Debe crear correctamente usando as_form"""

        area = AreaCreate.as_form(
            name="Finanzas"
        )

        assert area.name == "Finanzas"


class TestAreaResponse:

    def test_area_response_success(self):
        """Debe crear correctamente un AreaResponse"""

        response = AreaResponse(
            id=uuid4(),
            name="Tecnología"
        )

        assert response.name == "Tecnología"

    def test_area_response_invalid_uuid(self):
        """Debe fallar con UUID inválido"""

        with pytest.raises(ValidationError):

            AreaResponse(
                id="uuid-falso",
                name="Marketing"
            )

    def test_area_response_invalid_name(self):
        """Debe fallar si name tiene tipo inválido"""

        with pytest.raises(ValidationError):

            AreaResponse(
                id=uuid4(),
                name=999
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])