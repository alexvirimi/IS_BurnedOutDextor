# Esquemas para gestionar rangos y niveles de autorización.

from pydantic import BaseModel
from uuid import UUID
from fastapi import Form

class RankCreate(BaseModel):
    # Crear un nuevo rango con nombre y nivel
    rank_name: str
    level: int
    @classmethod
    def as_form(cls, rank_name: str = Form(...), level: int = Form(...)):
        return cls(rank_name=rank_name, level=level)
    
class RankResponse(BaseModel):
    # Respuesta con información de rango
    id: UUID
    rank_name: str
    level: int
    model_config = {"from_attributes": True}