from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from typing import List
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
    
class QuestionSurveyBulkCreate(BaseModel):
    id_survey: UUID
    questions: List[str]  
    
class AssignQuestions(BaseModel):
    id_survey: UUID
    question_ids: list[UUID]
    @classmethod
    def as_form(cls, id_survey: UUID, question_ids: list[UUID]):
        return cls(id_survey=id_survey, question_ids=question_ids)
    