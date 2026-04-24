from pydantic import BaseModel
from uuid import UUID

class RankCreate (BaseModel):                   # crea un rango cuyo único parámetro es el nombre
    rank_name: str
    
class RankResponse(BaseModel):
    id: UUID
    rank_name: str
    model_config = {"from_attributes": True}    # devuelve toda la información (id y nombre) de un rango
    