from pydantic import BaseModel
from uuid import UUID
from datetime import date 

class ResultCreate (BaseModel): #En el create va todo lo que se va a crear o recibir, no se pone el id de la tabla porque el UUID lo genera automaticamente
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_survey: UUID
    burnout_score: str
    generation_date: date
    
class ResultResponse(BaseModel): #En el response va todo lo que se va a mostrar, se pone el id de la tabla porque se va a mostrar, y se pone el model_config para que pueda convertir los atributos de la clase en atributos del modelo
    id: UUID
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_survey: UUID
    burnout_score: str
    generation_date: date
    model_config = {"from_attributes": True} 