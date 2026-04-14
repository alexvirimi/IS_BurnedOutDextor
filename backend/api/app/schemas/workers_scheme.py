from pydantic import BaseModel
from uuid import UUID

class WorkerCreate(BaseModel):
    name: str
    last_names: str
    age: int
    gender: str
    id_group: UUID
    id_rank: UUID
    
class WorkerResponse(BaseModel):
    id: UUID
    name: str
    last_names: str
    age: int
    gender: str
    id_group: UUID
    id_rank: UUID
    model_config = {"from_attributes": True} # toda la info de un trabajador