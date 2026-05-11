# Módulo de endpoints de autenticación del sistema.
# Proporciona rutas para registro, login, logout y obtener datos del usuario actual.

import os

from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db

from app.servicemodels.auth_user_service import AuthUserService
from app.servicemodels.workers_service import WorkerService

from app.schemas.auth_scheme import (
    AuthUserCreate,
    LoginRequest,
    LoginResponse,
    AuthUserResponse,
    CurrentUserData
)

from app.deps.auth_deps import get_current_user

from app.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# True in production (HTTPS), False in local dev (HTTP)
IS_PRODUCTION = (
    os.getenv("ENVIRONMENT", "development").lower()
    == "production"
)


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    payload: AuthUserCreate = Depends(AuthUserCreate.as_form),
    db: Session = Depends(get_db)
):

    auth_service = AuthUserService(db)

    worker_service = WorkerService(db)

    worker = worker_service.get_worker(payload.worker_id)

    if not worker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El trabajador con ID {payload.worker_id} no existe"
        )

    if auth_service.username_exists(payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El username '{payload.username}' ya está en uso"
        )

    new_auth_user = auth_service.register_user(
        payload.model_dump()
    )

    return new_auth_user


@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    payload: LoginRequest = Depends(LoginRequest.as_form),
    db: Session = Depends(get_db)
):

    auth_service = AuthUserService(db)

    auth_user = auth_service.login_user(
        payload.username,
        payload.password
    )

    if not auth_user:
        raise HTTPException(
            status_code=401,
            detail="Username o contraseña incorrectos"
        )

    user_info = auth_service.get_auth_user_with_worker_info(
        auth_user.id
    )

    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="No se pudo obtener la información del usuario"
        )

    # JWT payload COMPLETO
    token_payload = {
        "worker_id": str(user_info["worker_id"]),
        "username": user_info["username"],
        "rank_level": user_info["rank_level"],
        "rank_name": user_info["rank_name"],
        "id_group": str(user_info["id_group"]),
    }

    token = create_access_token(token_payload)

    response = JSONResponse(
        content={
            "message": "Login exitoso",
            "access_token": token,
            "worker_id": str(user_info["worker_id"]),
            "rank_level": user_info["rank_level"],
            "rank_name": user_info["rank_name"],
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite="lax",
        max_age=3600,
        path="/",
    )

    return response


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    """
    Clears the access_token cookie.
    No auth dependency — logout must work even with an expired or missing token.
    """
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax",      # must match the attributes used when setting it
        secure=IS_PRODUCTION,
    )
    return {"message": "Sesión cerrada exitosamente"}


@router.get(
    "/me",
    status_code=status.HTTP_200_OK
)
def get_current_user_info(
    current_user: CurrentUserData = Depends(get_current_user)
):

    return current_user