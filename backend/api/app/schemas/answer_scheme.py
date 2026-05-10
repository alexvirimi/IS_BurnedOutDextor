# Esquemas para gestionar respuestas de encuestas.

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from app.dbmodels.answer import AnswerEnum
from fastapi import Form

class AnswerCreate(BaseModel):
    """Schema para RRHH creando respuestas manualmente"""
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_question_survey: UUID
    value: AnswerEnum
    created_at: date = Field(default_factory=date.today)
    @classmethod
    def as_form(cls, id_worker: UUID = Form(...), id_group: UUID = Form(...), id_area: UUID = Form(...), id_question_survey: UUID = Form(...), value: AnswerEnum = Form(...)):
        return cls(id_worker=id_worker, id_group=id_group, id_area=id_area, id_question_survey=id_question_survey, value=value)

class AnswerUserCreate(BaseModel):
    """Schema optimizado para usuarios comunes respondiendo encuestas"""
    id_question_survey: UUID = Field(..., description="UUID de la pregunta en la encuesta")
    value: AnswerEnum = Field(..., description="Respuesta (1-5)")
    
    @classmethod
    def as_form(cls, id_question_survey: UUID = Form(...), value: AnswerEnum = Form(...)):
        return cls(id_question_survey=id_question_survey, value=value)

class AnswerResponse(BaseModel):
    # Respuesta de una encuesta completada
    id: UUID
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_question_survey: UUID
    value: AnswerEnum
    created_at: date
    model_config = {"from_attributes": True}

class BulkAnswerItem(BaseModel):
    # Un item de respuesta dentro del bulk
    id_question_survey: UUID
    value: AnswerEnum

class BulkAnswerCreate(BaseModel):
    # Crear múltiples respuestas de una vez (usuario respondiendo encuesta)
    id_survey: UUID = Field(..., description="UUID de la encuesta")
    answers: list[BulkAnswerItem] = Field(..., description="Lista de respuestas a preguntas")
    
    @classmethod
    def as_form(cls, id_survey: UUID = Form(...)):
        # El bulk se envía como JSON en el body, no como form
        return cls(id_survey=id_survey, answers=[])
    