# Esquemas para gestionar resultados de encuestas.

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from fastapi import Form

class ResultCreate(BaseModel):
    # Crear resultado de encuesta con score de burnout
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_survey: UUID
    burnout_score: str
    generation_date: date = Field(default_factory=date.today)
    @classmethod
    def as_form(cls, id_worker: UUID = Form(...), id_group: UUID = Form(...), id_area: UUID = Form(...), id_survey: UUID = Form(...), burnout_score: str = Form(...)):
        return cls(id_worker=id_worker, id_group=id_group, id_area=id_area, id_survey=id_survey, burnout_score=burnout_score)
    
class ResultResponse(BaseModel):
    # Respuesta con resultado completo de encuesta
    id: UUID
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_survey: UUID
    burnout_score: str
    generation_date: date
    model_config = {"from_attributes": True} 