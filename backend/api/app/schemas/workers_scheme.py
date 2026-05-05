from typing import Optional
from fastapi import Form
from pydantic import BaseModel
from uuid import UUID

class WorkerCreate(BaseModel):
    name: str
    last_names: str
    age: int
    gender: str
    id_group: UUID
    id_rank: UUID
    @classmethod
    def as_form(cls, 
                name: str = Form(...), 
                last_names: str = Form(...), 
                age: int = Form(...),
                gender: str = Form(...),
                id_group: UUID = Form(...),
                id_rank: UUID = Form(...)):
        return cls(
            name=name,
            last_names=last_names,
            age=age,
            gender=gender,
            id_group=id_group,
            id_rank=id_rank
        )

class WorkerDetailResponse(BaseModel):
    id: UUID
    name: str
    last_names: str
    age: int
    gender: str
    flag: bool
    id_group: Optional[UUID] = None
    id_rank: Optional[UUID] = None
    group: Optional[str] = None
    rank: Optional[str] = None
    model_config = {"from_attributes": True} 
class WorkerResponse(BaseModel):
    id: UUID
    name: str
    last_names: str
    age: int
    gender: str
    flag: bool
    id_group: UUID
    id_rank: UUID
    model_config = {"from_attributes": True} 