# Este archivo contiene los esquemas Pydantic para la autenticación y autorización del sistema.

from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from fastapi import Form

class AuthUserCreate(BaseModel):
    worker_id: UUID
    username: str
    password: str

    @classmethod
    def as_form(
        cls,
        worker_id: UUID = Form(..., description="UUID del trabajador existente"),
        username: str = Form(..., description="Nombre de usuario único"),
        password: str = Form(..., description="Contraseña")
    ):
        return cls(worker_id=worker_id, username=username, password=password)


class AuthUserResponse(BaseModel):
    id: UUID
    worker_id: UUID
    username: str
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(..., description="Nombre de usuario"),
        password: str = Form(..., description="Contraseña")
    ):
        return cls(username=username, password=password)


class LoginResponse(BaseModel):
    worker_id: UUID
    rank_level: int
    rank_name: str
    auth_user_id: Optional[UUID] = None  # incluido para compatibilidad con tests


class CurrentUserData(BaseModel):
    auth_user_id: Optional[UUID] = None  # presente en JWT tras login
    worker_id: UUID
    username: str
    id_group: UUID
    rank_level: int
    rank_name: str
    model_config = {"from_attributes": True}
