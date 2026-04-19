from pydantic import BaseModel
from uuid import UUID
from datetime import date 
from app.dbmodels.answer import AnswerEnum
class AnswerCreate (BaseModel):
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_question_survey: UUID
    value: AnswerEnum
    created_at: date

class AnswerBulkCreate(BaseModel):
        answers: list[AnswerCreate] #Un trabajador puede responder varias preguntas, por lo que se crea un endpoint para crear varias respuestas a la vez.
        
class AnswerResponse(BaseModel):
    id: UUID
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_question_survey: UUID
    value: AnswerEnum
    created_at: date
    model_config = {"from_attributes": True} 
    
    