from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth_scheme import CurrentUserData
from typing import List
from app.security import decode_access_token

# Swagger/OpenAPI security scheme
auth_scheme = APIKeyCookie(
    name="access_token",
    description="JWT token generado en /auth/login",
    auto_error=False
)

async def get_current_user(
    access_token: str = Security(auth_scheme),
    db: Session = Depends(get_db)
) -> CurrentUserData:

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No autenticado"
        )

    payload = decode_access_token(access_token)

    return CurrentUserData(**payload)


def require_role(allowed_levels: List[int]):

    async def check_role(
        current_user: CurrentUserData = Depends(get_current_user)
    ) -> CurrentUserData:

        if current_user.rank_level not in allowed_levels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso. Nivel requerido: {allowed_levels}"
            )

        return current_user

    return check_role


def require_comun(
    current_user: CurrentUserData = Depends(require_role([1]))
):
    return current_user


def require_lider(
    current_user: CurrentUserData = Depends(require_role([2]))
):
    return current_user


def require_rrhh(
    current_user: CurrentUserData = Depends(require_role([3]))
):
    return current_user


def require_lider_or_rrhh(
    current_user: CurrentUserData = Depends(require_role([2, 3]))
):
    return current_user


def require_any_authenticated(
    current_user: CurrentUserData = Depends(require_role([1, 2, 3]))
):
    return current_user