from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from app.dbmodels.answer import AnswerEnum
from fastapi import Form
class AnswerCreate (BaseModel):
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_question_survey: UUID
    value: AnswerEnum
    created_at: date = Field(default_factory=date.today) # Auto fecha yupi
    @classmethod
    def as_form(cls, id_worker: UUID = Form(...), id_group: UUID = Form(...), id_area: UUID = Form(...), id_question_survey: UUID = Form(...), value: AnswerEnum = Form(...)):
        return cls(id_worker=id_worker, id_group=id_group, id_area=id_area, id_question_survey=id_question_survey, value=value)

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
    
    