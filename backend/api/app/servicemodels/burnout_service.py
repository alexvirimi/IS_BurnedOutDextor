"""
Servicio de Burnout: Nexo entre API (8000) e IA Service (8001).
"""

import os

from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

import httpx

from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.burnout_integration_scheme import (
    BurnoutPredictionResponse
)

# Configuración AI Service
AI_URL = os.getenv(
    "AI_SERVICE_URL",
    "http://localhost:8001/predict"
)


class BurnoutService:

    @staticmethod
    def get_worker_features(
        db: Session,
        worker_id: UUID
    ):

        query = text("""
            SELECT *
            FROM vw_worker_burnout_features
            WHERE worker_id = :worker_id
        """)

        result = db.execute(
            query,
            {"worker_id": str(worker_id)}
        ).mappings().first()

        if not result:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron features del trabajador"
            )

        return dict(result)

    @staticmethod
    async def predict_worker_burnout(
        db: Session,
        worker_id: UUID,
        survey_id: UUID
    ) -> BurnoutPredictionResponse:

        # Obtener features
        features = BurnoutService.get_worker_features(
            db,
            worker_id
        )

        # Validar NULLs
        for key, value in features.items():

            if value is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"El campo '{key}' es NULL"
                )

        # Convertir tipos no serializables
        for key, value in features.items():

            if isinstance(value, UUID):
                features[key] = str(value)

            elif isinstance(value, Decimal):
                features[key] = float(value)

            elif isinstance(value, datetime):
                features[key] = value.isoformat()

            elif isinstance(value, date):
                features[key] = value.isoformat()

            elif isinstance(value, Enum):
                features[key] = value.value

        # Agregar survey_id
        features["survey_id"] = str(survey_id)

        # Convertir TODO a JSON serializable
        features = jsonable_encoder(features)

        try:

            async with httpx.AsyncClient() as client:

                response = await client.post(
                    AI_URL,
                    json=features,
                    timeout=30.0
                )

                print("STATUS:", response.status_code)
                print("BODY:", response.text)

                response.raise_for_status()

                data = response.json()

                return BurnoutPredictionResponse(**data)

        except httpx.ConnectError:

            raise HTTPException(
                status_code=503,
                detail="AI Service no disponible"
            )

        except httpx.HTTPStatusError as exc:

            raise HTTPException(
                status_code=502,
                detail=exc.response.text
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=str(e)
            )