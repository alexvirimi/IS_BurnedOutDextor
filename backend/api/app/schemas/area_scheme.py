# Esquemas para gestionar áreas de la empresa.

from pydantic import BaseModel
from uuid import UUID
from fastapi import Form

class AreaCreate(BaseModel):
    name:str
    @classmethod
    def as_form(cls, name: str = Form(...)):
        return cls(name=name)
class AreaResponse(BaseModel):
    # Respuesta de información de área
    id: UUID
    name: str
    model_config = {"from_attributes": True} 