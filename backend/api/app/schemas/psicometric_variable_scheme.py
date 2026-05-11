from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

class PsicometricVariableBase(BaseModel):
    name: str = Field(..., description="Nombre de la variable psicométrica (agotamiento, despersonalización, eficacia)")

class PsicometricVariableCreate(PsicometricVariableBase):
    pass

class PsicometricVariableUpdate(PsicometricVariableBase):
    name: Optional[str] = Field(None, description="Nombre de la variable psicométrica (agotamiento, despersonalización, eficacia)")

class PsicometricVariableResponse(PsicometricVariableBase):
    id: UUID

    model_config = {"from_attributes": True}