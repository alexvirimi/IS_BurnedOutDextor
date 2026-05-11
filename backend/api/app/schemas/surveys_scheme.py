# Esquemas para gestionar encuestas.

from fastapi import Form
from pydantic import BaseModel, field_validator, model_validator
from uuid import UUID
from datetime import date
from typing import Literal, Optional
from app.schemas.psicometric_variable_scheme import PsicometricVariableResponse


class SurveyCreate(BaseModel):
    # Crear nueva encuesta con fechas y estado
    name: str
    aperture_date: date
    finishing_date: date
    status: str

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        aperture_date: date = Form(...),
        finishing_date: date = Form(...),
        status: str = Form(...),
    ):
        return cls(
            name=name,
            aperture_date=aperture_date,
            finishing_date=finishing_date,
            status=status,
        )


class SurveyUpdate(BaseModel):
    """
    Actualización parcial de encuesta.
    Todos los campos son opcionales — solo los que se envíen se modificarán.
    """
    name: Optional[str] = None
    aperture_date: Optional[date] = None
    finishing_date: Optional[date] = None
    status: Optional[Literal["activa", "finalizada"]] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v

    @model_validator(mode="after")
    def dates_coherent(self) -> "SurveyUpdate":
        if (
            self.aperture_date is not None
            and self.finishing_date is not None
            and self.finishing_date < self.aperture_date
        ):
            raise ValueError(
                "La fecha de cierre no puede ser anterior a la fecha de apertura"
            )
        return self

    @model_validator(mode="after")
    def at_least_one_field(self) -> "SurveyUpdate":
        if all(
            v is None
            for v in (self.name, self.aperture_date, self.finishing_date, self.status)
        ):
            raise ValueError("Debes enviar al menos un campo para actualizar")
        return self


class QuestionInSurvey(BaseModel):
    id: UUID
    text: str
    psicometric_variable: PsicometricVariableResponse
    model_config = {"from_attributes": True}


class SurveyWithQuestions(BaseModel):
    id: UUID
    name: str
    questions: list[QuestionInSurvey]
    model_config = {"from_attributes": True}


class SurveyResponse(BaseModel):
    id: UUID
    name: str
    aperture_date: date
    finishing_date: date
    status: str
    model_config = {"from_attributes": True}


class AnswerOption(BaseModel):
    value: int
    label: str
    model_config = {"from_attributes": True}


class QuestionComplete(BaseModel):
    id: UUID
    question_text: str
    psicometric_variable: str
    model_config = {"from_attributes": True}


class SurveyComplete(BaseModel):
    id: UUID
    name: str
    aperture_date: date
    finishing_date: date
    status: str
    questions: list[QuestionComplete]
    answer_options: list[AnswerOption]
    model_config = {"from_attributes": True}
