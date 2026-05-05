from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth_scheme import CurrentUserData
from typing import Optional, List
from uuid import UUID

# Define el esquema de seguridad para Swagger
auth_scheme = APIKeyHeader(
    name="auth-user-id",
    description="ID de sesión obtenido del endpoint /auth/login",
    auto_error=False
)

# Sistema de sesiones en memoria (producción usaría Redis/JWT)
_active_sessions = {}

def set_user_session(auth_user_id: UUID, user_data: dict):
    """Establece una sesión activa para un usuario autenticado."""
    _active_sessions[str(auth_user_id)] = user_data

def get_user_session(auth_user_id: str) -> Optional[dict]:
    """Recupera la sesión activa de un usuario."""
    return _active_sessions.get(auth_user_id)

def clear_user_session(auth_user_id: UUID):
    """Limpia la sesión de un usuario (logout)."""
    _active_sessions.pop(str(auth_user_id), None)

async def get_current_user(
    auth_user_id: str = Depends(auth_scheme),  # Usa el scheme de seguridad
    db: Session = Depends(get_db)
) -> CurrentUserData:
    """
    Dependencia que valida que el usuario esté autenticado.
    Extrae el auth_user_id del header y verifica que tenga una sesión activa.
    """
    
    if not auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó credencial de autenticación"
        )
    
    # Busca la sesión activa del usuario
    user_session = get_user_session(auth_user_id)
    
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado. Por favor, realiza login primero."
        )
    
    return CurrentUserData(**user_session)

def require_role(allowed_levels: List[int]):
    """Factory que crea una dependencia para verificar roles específicos."""
    
    async def check_role(current_user: CurrentUserData = Depends(get_current_user)) -> CurrentUserData:
        if current_user.rank_level not in allowed_levels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso. Nivel requerido: {allowed_levels}, Tu nivel: {current_user.rank_level}"
            )
        return current_user
    
    return check_role

# Dependencias específicas por rol
def require_comun(current_user: CurrentUserData = Depends(require_role([1]))):
    return current_user

def require_lider(current_user: CurrentUserData = Depends(require_role([2]))):
    return current_user

def require_rrhh(current_user: CurrentUserData = Depends(require_role([3]))):
    return current_user

def require_lider_or_rrhh(current_user: CurrentUserData = Depends(require_role([2, 3]))):
    return current_user

def require_any_authenticated(current_user: CurrentUserData = Depends(require_role([1, 2, 3]))):
    return current_user