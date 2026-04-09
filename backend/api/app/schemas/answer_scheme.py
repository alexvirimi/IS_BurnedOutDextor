from pydantic import BaseModel
from uuid import UUID

class AnswerCreate (BaseModel):
    name:str
    
class AreaResponse(BaseModel):
    id: UUID
    name: str
    model_config = {"from_attributes": True} 