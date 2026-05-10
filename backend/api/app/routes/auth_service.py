# Módulo de endpoints de autenticación del sistema.
# Proporciona rutas para registro, login, logout y obtener datos del usuario actual.

from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.auth_user_service import AuthUserService
from app.servicemodels.workers_service import WorkerService
from app.schemas.auth_scheme import AuthUserCreate, LoginRequest, LoginResponse, AuthUserResponse
from app.deps.auth_deps import set_user_session, get_current_user, clear_user_session
from app.schemas.auth_scheme import CurrentUserData
from core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthUserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: AuthUserCreate = Depends(AuthUserCreate.as_form),  # ✅ Form-data
    db: Session = Depends(get_db)
):
    # Registra un nuevo usuario autenticado en el sistema.
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


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest = Depends(LoginRequest.as_form), db: Session = Depends(get_db)):
    auth_service = AuthUserService(db)
    auth_user = auth_service.login_user(payload.username, payload.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Username o contraseña incorrectos")

    user_info = auth_service.get_auth_user_with_worker_info(auth_user.id)
    if not user_info:
        raise HTTPException(status_code=401, detail="No se pudo obtener la información del usuario")

    token = create_access_token(user_info)

    response = JSONResponse(content={
        "worker_id": str(user_info["worker_id"]),
        "rank_level": user_info["rank_level"],
        "rank_name": user_info["rank_name"],
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,        # JS cannot read this — blocks XSS token theft
        secure=True,          # HTTPS only
        samesite="strict",    # Blocks CSRF from cross-origin requests
        max_age=3600,
        path="/",
    )
    return response


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    current_user: CurrentUserData = Depends(get_current_user),
):
    response.delete_cookie("access_token", path="/")
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_user_info(
    current_user: CurrentUserData = Depends(get_current_user)
):
    # Retorna la información del usuario autenticado actual.
    return current_user