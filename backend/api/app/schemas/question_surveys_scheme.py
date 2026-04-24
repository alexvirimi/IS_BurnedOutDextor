from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class QuestionSurveyCreate(BaseModel):
    id_survey: UUID
    id_question: UUID

class QuestionSurveyUpdate(BaseModel):                # para actualizar una pregunta, los campos son opcionales para permitir actualizaciones parciales
    text: Optional[str] = None                  # El optional es para que se puedan mandar unos si y otros no
    psicometric_variable: Optional[str] = None

class QuestionSurveyResponse(BaseModel):
    id: UUID
    id_survey: UUID
    id_question: UUID
    model_config = {"from_attributes": True}    # Devuelve todos los parametros de una relación entre preguntas y encuestas.