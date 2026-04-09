from pydantic import BaseModel
from uuid import UUID

class AreaCreate (BaseModel):
    name:str
    
class AreaResponse(BaseModel):
    id: UUID
    name: str
    model_config = {"from_attributes": True} 