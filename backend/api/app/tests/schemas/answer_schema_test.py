# Tests para los esquemas AnswerCreate y AnswerResponse

import pytest
from uuid import uuid4
from datetime import date
from pydantic import ValidationError
from app.schemas.answer_scheme import AnswerCreate, AnswerResponse
from app.dbmodels.answer import AnswerEnum


class TestAnswerCreate:

    def test_create_answer_success(self):
        """Debe crear correctamente un AnswerCreate válido"""

        answer = AnswerCreate(
        id_worker=uuid4(),
        id_group=uuid4(),
        id_area=uuid4(),
        id_question_survey=uuid4(),
        value=AnswerEnum.SIEMPRE
    )
        assert answer.id_worker is not None
        assert answer.id_group is not None
        assert answer.id_area is not None
        assert answer.id_question_survey is not None
        assert answer.value == AnswerEnum.SIEMPRE
        assert answer.created_at == date.today()

    def test_created_at_default(self):
        """Debe asignar automáticamente la fecha actual"""

        answer = AnswerCreate(
        id_worker=uuid4(),
        id_group=uuid4(),
        id_area=uuid4(),
        id_question_survey=uuid4(),
        value=AnswerEnum.SIEMPRE
        )

        assert answer.created_at == date.today()

    def test_invalid_uuid(self):
        """Debe fallar si un UUID es inválido"""

        with pytest.raises(ValidationError):

            AnswerCreate(
                id_worker="uuid-invalido",
                id_group=uuid4(),
                id_area=uuid4(),
                id_question_survey=uuid4(),
                value=AnswerEnum.CASI_SIEMPRE
            )

    def test_invalid_enum(self):
        """Debe fallar si el enum no existe"""

        with pytest.raises(ValidationError):

            AnswerCreate(
                id_worker=uuid4(),
                id_group=uuid4(),
                id_area=uuid4(),
                id_question_survey=uuid4(),
                value="respuesta_invalida"
            )

    def test_as_form_method(self):
        """Debe crear correctamente usando as_form"""

        answer = AnswerCreate.as_form(
            id_worker=uuid4(),
            id_group=uuid4(),
            id_area=uuid4(),
            id_question_survey=uuid4(),
            value=AnswerEnum.A_VECES
        )

        assert isinstance(answer, AnswerCreate)
        assert answer.value == AnswerEnum.A_VECES


class TestAnswerResponse:

    def test_answer_response_success(self):
        """Debe crear correctamente un AnswerResponse"""

        response = AnswerResponse(
            id=uuid4(),
            id_worker=uuid4(),
            id_group=uuid4(),
            id_area=uuid4(),
            id_question_survey=uuid4(),
            value=AnswerEnum.SIEMPRE,
            created_at=date.today()
        )

        assert response.id is not None
        assert response.value == AnswerEnum.SIEMPRE
        assert response.created_at == date.today()

    def test_answer_response_invalid_enum(self):
        """Debe fallar con enum inválido"""

        with pytest.raises(ValidationError):

            AnswerResponse(
                id=uuid4(),
                id_worker=uuid4(),
                id_group=uuid4(),
                id_area=uuid4(),
                id_question_survey=uuid4(),
                value="valor_fake",
                created_at=date.today()
            )

    def test_answer_response_invalid_date(self):
        """Debe fallar con fecha inválida"""

        with pytest.raises(ValidationError):

            AnswerResponse(
                id=uuid4(),
                id_worker=uuid4(),
                id_group=uuid4(),
                id_area=uuid4(),
                id_question_survey=uuid4(),
                value=AnswerEnum.CASI_SIEMPRE,
                created_at=12345
            )