# Este archivo contiene los esquemas Pydantic para la autenticación y autorización del sistema.
# Define los modelos para las solicitudes de registro y login, así como las respuestas que se
# retornan con la información del usuario autenticado, su rango y nivel de acceso.
# Estos esquemas validan y serializan los datos de autenticación entre el cliente y la API.

from pydantic import BaseModel
from uuid import UUID
from fastapi import Form

class AuthUserCreate(BaseModel):
    """Esquema para la solicitud de registro."""
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
    """Esquema para la respuesta de autenticación."""
    id: UUID
    worker_id: UUID
    username: str
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Esquema para la solicitud de login."""
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
    """Esquema para la respuesta de login exitoso."""
    worker_id: UUID
    rank_level: int
    rank_name: str
    auth_user_id: UUID


class CurrentUserData(BaseModel):
    """Esquema que representa los datos del usuario actual autenticado."""
    auth_user_id: UUID
    worker_id: UUID
    username: str
    rank_level: int
    rank_name: str
    id_group: UUID
    model_config = {"from_attributes": True}