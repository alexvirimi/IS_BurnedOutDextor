from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth_scheme import CurrentUserData
from typing import List, Optional
from app.security import decode_access_token

# ─── Swagger / OpenAPI security schemes ───────────────────────────────────────
#
# TWO schemes are declared here:
#
# 1. cookie_scheme  (APIKeyCookie, auto_error=False)
#    Used ONLY so that Swagger UI shows the padlock on protected endpoints.
#    auto_error=False means FastAPI will NOT automatically reject requests that
#    lack this header — that responsibility stays with get_current_user below.
#    This is correct: Swagger cannot send HttpOnly cookies, so we must not let
#    the scheme itself block every Swagger "Try it out" call.
#
# 2. bearer_scheme  (HTTPBearer, auto_error=False)
#    Used as a fallback for cross-origin fetch() calls where samesite="lax"
#    prevents the cookie from being forwarded (e.g. DELETE / PATCH from a
#    different origin during local dev).  The frontend stores the raw JWT in
#    memory (setApiToken) and injects it as Authorization: Bearer <token>.
#
# Neither scheme raises on its own.  get_current_user always makes the
# final call on whether the request is authenticated.

cookie_scheme = APIKeyCookie(
    name="access_token",
    description="HttpOnly JWT cookie set by POST /auth/login",
    auto_error=False,   # must stay False — see note above
)

bearer_scheme = HTTPBearer(
    description="Bearer JWT for cross-origin requests (dev fallback)",
    auto_error=False,   # must stay False — same reason
)


# ─── Core dependency ──────────────────────────────────────────────────────────

async def get_current_user(
    request: Request,
    cookie_token: Optional[str] = Depends(cookie_scheme),
    bearer_creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUserData:
    """
    Resolves the current user from either:
      • the HttpOnly 'access_token' cookie  (normal browser requests), or
      • the Authorization: Bearer header    (cross-origin dev / Swagger UI).

    Raises 401 if neither is present or if the token is invalid/expired.
    Raises 401 (not 403) here; role checks raise 403 via require_role().
    """

    # 1. Prefer the cookie (set by the server, most secure).
    token: Optional[str] = cookie_token

    # 2. Fall back to Bearer header (frontend memory token / Swagger UI).
    if not token and bearer_creds:
        token = bearer_creds.credentials

    # 3. Nothing found → not authenticated.
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    # 4. Decode and validate the JWT.
    #    decode_access_token() raises HTTP 401 on any JWTError.
    payload = decode_access_token(token)

    return CurrentUserData(**payload)


# ─── Role guards ──────────────────────────────────────────────────────────────

def require_role(allowed_levels: List[int]):
    """
    Returns a FastAPI dependency that enforces a minimum rank level.
    Must be used *after* get_current_user in the dependency chain.
    """

    async def check_role(
        current_user: CurrentUserData = Depends(get_current_user),
    ) -> CurrentUserData:
        if current_user.rank_level not in allowed_levels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso. Nivel requerido: {allowed_levels}",
            )
        return current_user

    return check_role


def require_comun(
    current_user: CurrentUserData = Depends(require_role([1])),
) -> CurrentUserData:
    return current_user


def require_lider(
    current_user: CurrentUserData = Depends(require_role([2])),
) -> CurrentUserData:
    return current_user


def require_rrhh(
    current_user: CurrentUserData = Depends(require_role([3])),
) -> CurrentUserData:
    return current_user


def require_lider_or_rrhh(
    current_user: CurrentUserData = Depends(require_role([2, 3])),
) -> CurrentUserData:
    return current_user


def require_any_authenticated(
    current_user: CurrentUserData = Depends(require_role([1, 2, 3])),
) -> CurrentUserData:
    return current_user


# ─── Legacy session helpers (kept for backwards compatibility) ─────────────────
# These were referenced in some older route files.  They are no-ops now that
# session management is fully JWT-based.

def set_user_session(*args, **kwargs):  # type: ignore[override]
    pass


def clear_user_session(*args, **kwargs):  # type: ignore[override]
    pass
