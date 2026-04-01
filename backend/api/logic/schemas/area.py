"""
📝 ARCHIVO DE PRUEBA
Este archivo contiene esquemas Pydantic para la tabla Area.
Úsalo para validar entrada/salida de datos en endpoints.
⚠️ Si cambias la lógica de Area, actualiza estos esquemas.
"""

from pydantic import BaseModel
from typing import Optional
import uuid


class AreaBase(BaseModel):
    """Schema base para Area - Contiene campos comunes"""
    name: str


class AreaCreate(AreaBase):
    """Schema para crear un Area"""
    pass


class AreaUpdate(BaseModel):
    """Schema para actualizar un Area"""
    name: Optional[str] = None


class AreaResponse(AreaBase):
    """Schema para respuesta de Area"""
    id: uuid.UUID
    
    class Config:
        from_attributes = True
