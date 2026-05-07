from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date 
from fastapi import Form
class ResultCreate (BaseModel): #En el create va todo lo que se va a crear o recibir, no se pone el id de la tabla porque el UUID lo genera automaticamente
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_survey: UUID
    burnout_score: str
    generation_date: date = Field(default_factory=date.today)
    @classmethod
    def as_form(cls, id_worker: UUID = Form(...), id_group: UUID = Form(...), id_area: UUID = Form(...), id_survey: UUID = Form(...), burnout_score: str = Form(...)):
        return cls(id_worker=id_worker, id_group=id_group, id_area=id_area, id_survey=id_survey, burnout_score=burnout_score)
    
class ResultResponse(BaseModel): #En el response va todo lo que se va a mostrar, se pone el id de la tabla porque se va a mostrar, y se pone el model_config para que pueda convertir los atributos de la clase en atributos del modelo
    id: UUID
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_survey: UUID
    burnout_score: str
    generation_date: date
    model_config = {"from_attributes": True} 