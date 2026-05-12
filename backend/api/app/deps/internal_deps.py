import os

from fastapi import (
    Header,
    HTTPException
)

API_KEY = os.getenv("API_KEY")


def verify_internal_api_key(
    authorization: str = Header(None)
):

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Authorization header faltante"
        )

    expected = f"Bearer {API_KEY}"

    if authorization != expected:

        raise HTTPException(
            status_code=403,
            detail="API key inválida"
        )