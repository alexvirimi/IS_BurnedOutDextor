from pydantic import BaseModel
from uuid import UUID
from datetime import date 

class AnswerCreate (BaseModel):
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_question_survey: UUID
    value: int
    created_at: date
    
class AnswerResponse(BaseModel):
    id: UUID
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_question_survey: UUID
    value: int
    created_at: date
    model_config = {"from_attributes": True} 