from pydantic import BaseModel
from uuid import UUID
from datetime import date 

class SurveyCreate(BaseModel):
    name: str
    apreture_date: date
    finishing_date: date
    status: str

class QuestionInSurvey(BaseModel):
    id_question_survey: UUID
    question_text: str
    psicometric_variable: str
    model_config = {"from_attributes": True}

class SurveyWithQuestions(BaseModel):
    id: UUID
    name: str
    questions: list[QuestionInSurvey]
    model_config = {"from_attributes": True}
    
#Estas dos clases son para el endpoint que obtiene una encuesta con sus preguntas, y la otra es para obtener solo la información de la encuesta sin las preguntas
#Seran muy utiles para Alex cuando quiera mostrar la información de la encuesta sin necesidad de mostrar las preguntas, y para mostrar la información de la encuesta con sus preguntas cuando quiera mostrar la información completa de la encuesta.
#De nada Alex

class SurveyResponse(BaseModel):
    id: UUID
    name: str
    apreture_date: date
    finishing_date: date
    status: str
    model_config = {"from_attributes": True}