# Esquemas para gestionar encuestas.

from fastapi import Form
from pydantic import BaseModel
from uuid import UUID
from datetime import date

class SurveyCreate(BaseModel):
    # Crear nueva encuesta con fechas y estado
    name: str
    aperture_date: date
    finishing_date: date
    status: str
    @classmethod
    def as_form(cls, 
                name: str = Form(...), 
                aperture_date: date = Form(...), 
                finishing_date: date = Form(...), 
                status: str = Form(...)):
        return cls(name=name, aperture_date=aperture_date, finishing_date=finishing_date, status=status)

class QuestionInSurvey(BaseModel):
    # Pregunta dentro de una encuesta
    id: UUID
    text: str
    psicometric_variable: str
    model_config = {"from_attributes": True}
    
class SurveyWithQuestions(BaseModel):
    # Encuesta con preguntas asociadas
    id: UUID
    name: str
    questions: list[QuestionInSurvey]
    model_config = {"from_attributes": True}


class SurveyResponse(BaseModel):
    # Respuesta con información de encuesta
    id: UUID
    name: str
    aperture_date: date
    finishing_date: date
    status: str
    model_config = {"from_attributes": True}

class AnswerOption(BaseModel):
    # Opción de respuesta (escala 1-5)
    value: int
    label: str
    model_config = {"from_attributes": True}

class QuestionComplete(BaseModel):
    # Pregunta con su ID de relación pregunta-encuesta para poder responder
    id: UUID  # question_survey.id (necesario para responder)
    question_text: str
    psicometric_variable: str
    model_config = {"from_attributes": True}

class SurveyComplete(BaseModel):
    # Survey + todas sus preguntas + opciones de respuesta (listo para responder)
    id: UUID
    name: str
    aperture_date: date
    finishing_date: date
    status: str
    questions: list[QuestionComplete]
    answer_options: list[AnswerOption]  # Opciones comunes 1-5
    model_config = {"from_attributes": True}