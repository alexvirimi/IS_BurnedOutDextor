"""
Este módulo define todos los endpoints relacionados con autenticación del sistema.
Proporciona rutas para registro de nuevos usuarios autenticados (register) y login de usuarios existentes.
El endpoint POST /register crea un nuevo registro en la tabla auth_user vinculado a un trabajador existente.
El endpoint POST /login valida credenciales y establece una sesión activa para el usuario.
Ambos endpoints retornan información relevante en formato JSON, incluyendo detalles del rango y nivel de acceso.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.auth_user_service import AuthUserService
from app.servicemodels.workers_service import WorkerService
from app.schemas.auth_scheme import AuthUserCreate, LoginRequest, LoginResponse, AuthUserResponse
from app.deps.auth_deps import set_user_session, get_current_user, clear_user_session
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

# Crea el router para todas las rutas de autenticación
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: AuthUserCreate = Depends(AuthUserCreate.as_form),  # ✅ Form-data
    db: Session = Depends(get_db)
):
    """
    Endpoint para registrar un nuevo usuario autenticado.
    
    Requiere (form-data):
        - worker_id: UUID del trabajador existente
        - username: Nombre de usuario único
        - password: Contraseña en texto plano
    
    Retorna:
        - AuthUserResponse con id, worker_id y username del usuario creado
    
    Errores posibles:
        - 400: El trabajador no existe o el username ya está en uso
        - 409: El username ya existe en el sistema
    """
    # Inicializa el servicio de autenticación
    auth_service = AuthUserService(db)
    
    # Verifica que el trabajador existe
    worker_service = WorkerService(db)
    worker = worker_service.get_worker(payload.worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El trabajador con ID {payload.worker_id} no existe"
        )
    
    # Verifica que el username no esté en uso
    if auth_service.username_exists(payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El username '{payload.username}' ya está en uso. Elige otro."
        )
    
    # Crea el nuevo usuario autenticado
    new_auth_user = auth_service.register_user(payload.model_dump())
    
    # Retorna la información del usuario creado
    return new_auth_user

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(
    payload: LoginRequest = Depends(LoginRequest.as_form),  # ✅ Form-data
    db: Session = Depends(get_db)
):
    """
    Endpoint para autenticar un usuario y establecer una sesión.
    
    Requiere (form-data):
        - username: Nombre de usuario registrado
        - password: Contraseña en texto plano
    
    Retorna:
        - LoginResponse con worker_id, rank_level, rank_name y auth_user_id
        - El header 'auth_user_id' debe ser incluido en futuras solicitudes
    
    Errores posibles:
        - 401: Usuario no encontrado o contraseña incorrecta
    """
    # Inicializa el servicio de autenticación
    auth_service = AuthUserService(db)
    
    # Valida las credenciales del usuario
    auth_user = auth_service.login_user(payload.username, payload.password)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o contraseña incorrectos"
        )
    
    # Obtiene la información completa del usuario con su rango
    user_info = auth_service.get_auth_user_with_worker_info(auth_user.id)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo obtener la información del usuario"
        )
    
    # Establece la sesión activa para el usuario
    set_user_session(auth_user.id, user_info)
    
    # Retorna la información del usuario autenticado
    return LoginResponse(
        worker_id=user_info['worker_id'],
        rank_level=user_info['rank_level'],
        rank_name=user_info['rank_name'],
        auth_user_id=user_info['auth_user_id']
    )

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para cerrar la sesión del usuario autenticado.
    
    Requiere:
        - Header 'auth_user_id' con el ID del usuario autenticado
    
    Retorna:
        - Mensaje de confirmación
    
    Errores posibles:
        - 401: Usuario no autenticado
    """
    # Limpia la sesión del usuario
    clear_user_session(current_user.auth_user_id)
    
    # Retorna confirmación
    return {
        "message": "Sesión cerrada exitosamente",
        "user_id": str(current_user.auth_user_id)
    }

@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user_info(
    current_user: CurrentUserData = Depends(get_current_user)
):
    """
    Endpoint para obtener la información del usuario autenticado actualmente.
    
    Requiere:
        - Header 'auth_user_id' con el ID del usuario autenticado
    
    Retorna:
        - Información completa del usuario (auth_user_id, worker_id, username, rank_level, rank_name, id_group)
    
    Errores posibles:
        - 401: Usuario no autenticado
    """
    # Retorna los datos del usuario actual
    return current_user