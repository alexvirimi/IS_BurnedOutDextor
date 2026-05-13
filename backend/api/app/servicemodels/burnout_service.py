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

from sqlalchemy import text, func
from sqlalchemy.orm import Session

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.burnout_integration_scheme import (
    BurnoutPredictionResponse
)
from app.servicemodels.intervention_service import InterventionService
from app.dbmodels import Result

# Configuración AI Service
# Permitir que la variable de entorno sea la URL completa o sólo la base.
# Si la base no incluye "/predict" se añade automáticamente.
_ai_env = os.getenv("AI_SERVICE_URL", "http://localhost:8001/predict")
if _ai_env.rstrip("/").endswith("/predict"):
    AI_URL = _ai_env
else:
    AI_URL = _ai_env.rstrip("/") + "/predict"

# UUIDs canónicos de variables psicométricas (deben coincidir con los de la BD)
_PSICO_DESPERSONALIZACION = "7bfe6646-c400-4913-93ec-bcff12c67987"
_PSICO_EFICACIA           = "9b76e819-3e37-4d52-ad7d-00bbecdab3d0"
_PSICO_AGOTAMIENTO        = "c8dfdbb2-6761-4bb7-ab29-7b2c615e11a5"


class BurnoutService:

    @staticmethod
    def _compute_psicometric_avgs(
        db: Session,
        worker_id: UUID,
        survey_id: UUID,
    ) -> dict:
        """
        Calcula directamente desde la BD los promedios psicométricos
        (agotamiento, despersonalización, eficacia) filtrando por
        worker_id Y survey_id, de modo que siempre reflejan la encuesta
        activa y no mezclan respuestas de otras encuestas.

        Retorna un dict con las tres claves::
            {
                'avg_agotamiento':       float,  # 1-5
                'avg_despersonalizacion': float, # 1-5
                'eficacia_invertida':    float,  # 1-5
            }
        Si no hay respuestas para alguna variable se usa 1.0 como mínimo.
        """
        query = text("""
            SELECT
                pv.id::text                      AS psico_id,
                AVG(a.value::numeric)            AS avg_value
            FROM answer a
            JOIN question_survey  qs ON qs.id = a.id_question_survey
            JOIN question          q  ON q.id  = qs.id_question
            JOIN psicometric_variable pv ON pv.id = q.psicometric_variable_id
            WHERE a.id_worker = :worker_id
              AND qs.id_survey = :survey_id
              AND pv.id IN (
                    :id_desp,
                    :id_efic,
                    :id_agot
              )
            GROUP BY pv.id
        """)

        rows = db.execute(query, {
            "worker_id": str(worker_id),
            "survey_id": str(survey_id),
            "id_desp":   _PSICO_DESPERSONALIZACION,
            "id_efic":   _PSICO_EFICACIA,
            "id_agot":   _PSICO_AGOTAMIENTO,
        }).mappings().all()

        # Indexar por psico_id para acceso rápido
        avgs_by_id = {row["psico_id"]: float(row["avg_value"]) for row in rows}

        avg_agotamiento        = max(avgs_by_id.get(_PSICO_AGOTAMIENTO,        1.0), 1.0)
        avg_despersonalizacion = max(avgs_by_id.get(_PSICO_DESPERSONALIZACION, 1.0), 1.0)
        avg_eficacia_raw       = max(avgs_by_id.get(_PSICO_EFICACIA,           1.0), 1.0)
        # Eficacia invertida: 6 - promedio (1-5 → 5-1), clamped a [1, 5]
        eficacia_invertida     = max(min(6.0 - avg_eficacia_raw, 5.0), 1.0)

        return {
            "avg_agotamiento":        round(avg_agotamiento,        4),
            "avg_despersonalizacion": round(avg_despersonalizacion, 4),
            "eficacia_invertida":     round(eficacia_invertida,     4),
        }

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
        """
        Guarda la predicción completa en la tabla result.
        Incluye: clase, confianza, razones y sugerencia de intervención.
        Permite múltiples resultados si tienen fechas diferentes.
        """
        # Verificar si ya existe resultado para este worker y survey
        # (idempotency a nivel de aplicación: si existe, lo actualizamos)
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
            # Actualizar resultado existente
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
            # Insertar nuevo resultado
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

        # IDempotency: si ya existe un resultado para este worker+survey, retornar ese resultado
        try:
            existing = (
                db.query(Result)
                .filter(Result.id_worker == worker_id, Result.id_survey == survey_id)
                .order_by(Result.generation_date.desc())
                .first()
            )

            if existing:
                # Reconstruir la respuesta mínima a partir del registro en BD
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
            # En caso de error al leer el resultado existente, continuar con la predicción
            pass

        # Obtener features
        features = BurnoutService.get_worker_features(
            db,
            worker_id
        )

        # ── Recalcular promedios psicométricos directamente desde la BD ─────────
        # La vista vw_worker_burnout_features puede tener valores obsoletos o NULL
        # si mezcla respuestas de otras encuestas. Aquí sobreescribimos siempre
        # con el cálculo preciso filtrado por worker_id + survey_id.
        psico_avgs = BurnoutService._compute_psicometric_avgs(db, worker_id, survey_id)
        features["avg_agotamiento"]        = psico_avgs["avg_agotamiento"]
        features["avg_despersonalizacion"] = psico_avgs["avg_despersonalizacion"]
        features["eficacia_invertida"]     = psico_avgs["eficacia_invertida"]
        print(
            f"Promedios psicométricos recalculados: "
            f"agotamiento={psico_avgs['avg_agotamiento']}, "
            f"despersonalizacion={psico_avgs['avg_despersonalizacion']}, "
            f"eficacia_invertida={psico_avgs['eficacia_invertida']}"
        )

        # Manejar valores NULL restantes: reemplazar por defaults razonables
        null_keys = [k for k, v in features.items() if v is None]
        if null_keys:
            print(f"Warning: campos NULL encontrados: {null_keys} — se aplicarán valores por defecto")

        # Campos psicométricos ya tienen valor calculado; solo los demás numéricos
        numeric_defaults = {
            "assigned_tasks", "completed_tasks", "absences", "employee_calls",
            "completion_rate", "seniority_years", "age",
        }

        for key in null_keys:
            if key in {"avg_agotamiento", "avg_despersonalizacion", "eficacia_invertida"}:
                # Ya fueron calculados arriba; si aún son None algo falló — usar mínimo válido
                features[key] = 1.0
            elif key in numeric_defaults or key.endswith("_enc"):
                features[key] = 0
            else:
                # Fallback para cadenas u otros tipos
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

        # Agregar survey_id
        features["survey_id"] = str(survey_id)

        # Convertir TODO a JSON serializable
        features = jsonable_encoder(features)

        # Validar que el payload contiene los campos que el AI service espera
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

        # Imprimir payload (útil para debugging en logs)
        print("AI payload keys:", list(features.keys()))

        try:
            # Debug: mostrar la URL del AI service y el payload enviado
            print("AI_URL:", AI_URL)
            try:
                print("AI payload:", json.dumps(features, ensure_ascii=False))
            except Exception:
                print("AI payload: <no se pudo serializar a JSON>")
            # Llamar al ai-service
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

                # Guardar resultado en BD
                result_id, generation_date = BurnoutService._save_result(
                    db, worker_id, survey_id, ai_data, suggestion
                )

                # Retornar respuesta completa
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