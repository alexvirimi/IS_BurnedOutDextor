# Esquemas para gestionar relaciones pregunta-encuesta.

from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from fastapi import Form

class QuestionSurveyCreate(BaseModel):
    id_survey: UUID
    id_question: UUID
    @classmethod
    def as_form(cls, id_survey: UUID = Form(...), id_question: UUID = Form(...)):
        return cls(id_survey=id_survey, id_question=id_question)

class QuestionSurveyUpdate(BaseModel):
    # Actualizar relación pregunta-encuesta (campos opcionales)
    id_survey: Optional[UUID] = Field(None, description="ID de la encuesta")
    id_question: Optional[UUID] = Field(None, description="ID de la pregunta")
    @classmethod
    def as_form(cls, id_survey: Optional[UUID] = Form(None), id_question: Optional[UUID] = Form(None)):
        # Solo incluir campos que son diferentes de None
        data = {}
        if id_survey is not None:
            data['id_survey'] = id_survey
        if id_question is not None:
            data['id_question'] = id_question
        return cls(**data)

class QuestionSurveyResponse(BaseModel):
    # Respuesta de relación pregunta-encuesta
    id: UUID
    id_survey: UUID
    id_question: UUID
    model_config = {"from_attributes": True}
    
class QuestionSurveyBulkCreate(BaseModel):
    id_survey: UUID
    questions: List[str]  
    
class AssignQuestions(BaseModel):
    # Asignar múltiples preguntas a una encuesta
    id_survey: UUID
    question_ids: list[UUID]
    @classmethod
    def as_form(cls, id_survey: UUID, question_ids: list[UUID]):
        return cls(id_survey=id_survey, question_ids=question_ids)