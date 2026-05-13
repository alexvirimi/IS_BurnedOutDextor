"""
Servicio de Burnout: Nexo entre API (8000) e IA Service (8001).
"""

import os

from uuid import UUID
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

import httpx
import json

from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.burnout_integration_scheme import (
    BurnoutPredictionResponse
)
from app.servicemodels.intervention_service import InterventionService
from app.dbmodels import Result

# Configuración AI Service
_ai_env = os.getenv("AI_SERVICE_URL", "http://localhost:8001/predict")
if _ai_env.rstrip("/").endswith("/predict"):
    AI_URL = _ai_env
else:
    AI_URL = _ai_env.rstrip("/") + "/predict"

# ─── Fix B: defaults separados por rango válido ───────────────────────────────
# Los campos psicométricos tienen rango [1.0, 5.0] — nunca pueden ser 0.
# eficacia_invertida = 6 - avg_eficacia, así que si eficacia = 1 (mínima),
# eficacia_invertida = 5 (máximo riesgo) es el default conservador.
_PSICOMETRIC_NULL_DEFAULTS: dict[str, float] = {
    "avg_agotamiento":        1.0,
    "avg_despersonalizacion": 1.0,
    "eficacia_invertida":     5.0,
}

# Campos numéricos cuyo valor válido cuando son NULL es 0
_NUMERIC_ZERO_FIELDS: set[str] = {
    "assigned_tasks",
    "completed_tasks",
    "absences",
    "employee_calls",
    "completion_rate",
    "seniority_years",
    "age",
}


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
    def _save_result(
        db: Session,
        worker_id: UUID,
        survey_id: UUID,
        data: dict,
        suggestion: str,
    ) -> str:
        check_query = text("""
            SELECT id, generation_date FROM result
            WHERE id_worker = :worker_id 
            AND id_survey = :survey_id
        """)
        
        existing = db.execute(check_query, {
            "worker_id": str(worker_id),
            "survey_id": str(survey_id),
        }).mappings().first()
        
        if existing:
            update_query = text("""
                UPDATE result
                SET burnout_confidence = :burnout_confidence,
                    burnout_class = :burnout_class,
                    burnout_reasons = :burnout_reasons,
                    suggested_intervention = :suggested_intervention
                WHERE id_worker = :worker_id 
                AND id_survey = :survey_id 
                RETURNING id, generation_date
            """)
            
            result = db.execute(update_query, {
                "burnout_confidence": data["burnout_confidence"],
                "burnout_class": data["burnout_class"],
                "burnout_reasons": "\n".join(data.get("reasons", [])),
                "suggested_intervention": suggestion,
                "worker_id": str(worker_id),
                "survey_id": str(survey_id),
            }).mappings().first()
        else:
            query = text("""
                INSERT INTO result (
                    id,
                    burnout_confidence,
                    burnout_class,
                    burnout_reasons,
                    suggested_intervention,
                    intervention_status,
                    id_worker,
                    id_group,
                    id_area,
                    id_survey,
                    generation_date,
                    flag
                )
                SELECT
                    gen_random_uuid(),
                    :burnout_confidence,         
                    :burnout_class,
                    :burnout_reasons,
                    :suggested_intervention,
                    'Pendiente',
                    :worker_id,
                    w.id_group,
                    g.id_area,
                    :survey_id,
                    CURRENT_DATE,
                    false
                FROM worker w
                JOIN "group" g ON g.id = w.id_group
                WHERE w.id = :worker_id
                RETURNING id, generation_date
            """)

            result = db.execute(query, {
                "burnout_confidence": data["burnout_confidence"],
                "burnout_class": data["burnout_class"],
                "burnout_reasons": "\n".join(data.get("reasons", [])),
                "suggested_intervention": suggestion,
                "worker_id": str(worker_id),
                "survey_id": str(survey_id),
            }).mappings().first()

        db.commit()

        return str(result["id"]), result["generation_date"]

    @staticmethod
    async def predict_worker_burnout(
        db: Session,
        worker_id: UUID,
        survey_id: UUID
    ) -> BurnoutPredictionResponse:

        # Idempotency: si ya existe un resultado, retornarlo
        try:
            existing = (
                db.query(Result)
                .filter(Result.id_worker == worker_id, Result.id_survey == survey_id)
                .order_by(Result.generation_date.desc())
                .first()
            )

            if existing:
                reasons = []
                if existing.burnout_reasons:
                    reasons = existing.burnout_reasons.split("\n")

                return BurnoutPredictionResponse(
                    worker_id=worker_id,
                    burnout_class=existing.burnout_class,
                    burnout_confidence=float(existing.burnout_confidence),
                    probabilities={},
                    reasons=reasons,
                    suggestion=existing.suggested_intervention or "",
                )
        except Exception:
            pass

        # Obtener features
        features = BurnoutService.get_worker_features(db, worker_id)

        # ── Fix C: guard clause para datos psicométricos faltantes ────────────
        # Si alguno de los tres promedios MBI es NULL, el worker no respondió
        # todas las variables psicométricas. Predecir con 0 daría resultados
        # inválidos y además viola la restricción ge=1.0 del schema del AI service.
        psicometric_fields = [
            "avg_agotamiento",
            "avg_despersonalizacion",
            "eficacia_invertida",
        ]
        missing_psico = [f for f in psicometric_fields if features.get(f) is None]

        if missing_psico:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Datos psicométricos incompletos: faltan respuestas para "
                    f"{missing_psico}. El trabajador debe completar todas las "
                    f"preguntas de la encuesta antes de generar la predicción."
                ),
            )

        # Manejar valores NULL con defaults correctos por tipo de campo
        null_keys = [k for k, v in features.items() if v is None]
        if null_keys:
            print(f"Warning: campos NULL encontrados: {null_keys} — aplicando defaults")

        for key in null_keys:
            if key in _PSICOMETRIC_NULL_DEFAULTS:
                # ── Fix B: usar 1.0 / 5.0 según el campo, nunca 0 ────────────
                features[key] = _PSICOMETRIC_NULL_DEFAULTS[key]
            elif key in _NUMERIC_ZERO_FIELDS or key.endswith("_enc"):
                features[key] = 0
            else:
                features[key] = ""

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

        features["survey_id"] = str(survey_id)
        features = jsonable_encoder(features)

        required_fields = [
            "worker_id",
            "survey_id",
            "assigned_tasks",
            "completed_tasks",
            "absences",
            "employee_calls",
            "completion_rate",
            "seniority_years",
            "age",
            "gender_enc",
            "worker_type_enc",
            "location_enc",
            "avg_agotamiento",
            "avg_despersonalizacion",
            "eficacia_invertida",
        ]

        missing = [f for f in required_fields if f not in features]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Payload incompleto para AI Service, faltan campos: {missing}"
            )

        print("AI payload keys:", list(features.keys()))

        try:
            print("AI_URL:", AI_URL)
            try:
                print("AI payload:", json.dumps(features, ensure_ascii=False))
            except Exception:
                print("AI payload: <no se pudo serializar a JSON>")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    AI_URL,
                    json=features,
                    timeout=30.0
                )

                print("STATUS:", response.status_code)
                print("BODY:", response.text)
                print("RESPONSE HEADERS:", dict(response.headers))

                response.raise_for_status()

                ai_data = response.json()

                suggestion = InterventionService.generate_suggestion(
                    burnout_class=ai_data['burnout_class'],
                    reasons=ai_data['reasons'],
                    features=features
                )

                result_id, generation_date = BurnoutService._save_result(
                    db, worker_id, survey_id, ai_data, suggestion
                )

                return BurnoutPredictionResponse(
                    worker_id=ai_data["worker_id"],
                    burnout_class=ai_data["burnout_class"],
                    burnout_confidence=ai_data["burnout_confidence"],
                    probabilities=ai_data["probabilities"],
                    reasons=ai_data["reasons"],
                    suggestion=suggestion,
                )

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