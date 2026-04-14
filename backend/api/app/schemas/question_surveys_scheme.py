from pydantic import BaseModel
from uuid import UUID

class QuestionSurveyCreate(BaseModel):
    id_survey: UUID
    id_question: UUID
    
class QuestionSurveyResponse(BaseModel):
    id: UUID
    id_survey: UUID
    id_question: UUID
    model_config = {"from_attributes": True}    # Devuelve todos los parametros de una relación entre preguntas y encuestas.