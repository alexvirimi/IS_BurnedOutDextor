from typing import Optional

from pydantic import BaseModel
from uuid import UUID

class WorkerCreate(BaseModel):
    name: str
    last_names: str
    age: int
    gender: str
    id_group: UUID
    id_rank: UUID
    
class WorkerDetailResponse(BaseModel):
    id: UUID
    name: str

    id_rank: Optional[UUID] = None
    id_group: Optional[UUID] = None

    rank: Optional[str] = None
    group: Optional[str] = None
    model_config = {"from_attributes": True} 
class WorkerResponse(BaseModel):
    id: UUID
    name: str
    last_names: str
    age: int
    gender: str
    id_group: UUID
    id_rank: UUID
    model_config = {"from_attributes": True} 