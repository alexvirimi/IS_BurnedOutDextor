from pydantic import BaseModel
from uuid import UUID

class GroupCreate (BaseModel):
    name:str
    id_area: UUID
    id_leader: UUID
    
class GroupResponse(BaseModel):
    id: UUID
    name: str
    id_area: UUID
    id_leader: UUID
    model_config = {"from_attributes": True} 