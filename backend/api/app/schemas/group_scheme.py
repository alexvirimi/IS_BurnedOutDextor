from typing import Optional

from pydantic import BaseModel, field_validator
from uuid import UUID
from fastapi import Form
class GroupCreate (BaseModel):
    name:str
    id_area: UUID
    id_leader: Optional[UUID] = None
    @classmethod
    def as_form (cls, name: str = Form(...), id_area: UUID = Form(...), id_leader: Optional[UUID] = Form(None)):
        return cls(name=name, id_area=id_area, id_leader=id_leader)
    
class GroupUpdate(BaseModel):
    name: Optional[str] = None
    id_area: Optional[UUID] = None
    id_leader: Optional[UUID] = None  
    @classmethod
    def as_form(cls, name: Optional[str] = Form(None), id_area: Optional[UUID] = Form(None), id_leader: Optional[UUID] = Form(None)):
        return cls(name=name, id_area=id_area, id_leader=id_leader)

# Para asignar/cambiar líder
class GroupAssignLeader(BaseModel):
    id_leader: UUID
    @classmethod
    def as_form(cls, id_leader: UUID = Form(...)):        
        return cls(id_leader=id_leader)
    
class GroupResponse(BaseModel):
    id: UUID
    name: str
    id_area: UUID
    id_leader: Optional[UUID] = None
    model_config = {"from_attributes": True} 