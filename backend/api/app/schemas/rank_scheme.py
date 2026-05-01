from pydantic import BaseModel
from uuid import UUID
from fastapi import Form
class RankCreate (BaseModel):                   # crea un rango cuyo único parámetro es el nombre
    rank_name: str
    @classmethod
    def as_form(cls, rank_name: str = Form(...)):
        return cls(rank_name=rank_name)
    
class RankResponse(BaseModel):
    id: UUID
    rank_name: str
    model_config = {"from_attributes": True}    # devuelve toda la información (id y nombre) de un rango
    