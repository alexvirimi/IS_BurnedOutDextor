"""
Rutas para predicción de burnout.
Endpoints:
- POST /burnout/predict
- GET /burnout/features/{worker_id}
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.servicemodels.burnout_service import BurnoutService

from app.schemas.burnout_integration_scheme import (
    BurnoutPredictionRequest,
    BurnoutPredictionResponse
)

router = APIRouter(
    prefix="/burnout",
    tags=["Burnout IA"],
    responses={
        404: {"description": "Trabajador no encontrado"},
        503: {"description": "AI Service no disponible"},
    }
)


@router.post(
    "/predict",
    response_model=BurnoutPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predecir riesgo de burnout",
    description="""
    Obtiene predicción de riesgo de burnout para un trabajador.

    Flujo:
    1. Recibe worker_id y survey_id
    2. Consulta vw_worker_burnout_features
    3. Valida datos
    4. Envía al AI Service (puerto 8001)
    5. Retorna predicción

    Requisitos:
    - Trabajador debe tener registros en BD
    - AI Service debe estar corriendo en puerto 8001
    - Vista SQL debe estar creada
    """
)
async def predict_burnout(
    request: BurnoutPredictionRequest,
    db: Session = Depends(get_db),
) -> BurnoutPredictionResponse:
    """
    Endpoint principal para predicción de burnout.
    """

    return await BurnoutService.predict_worker_burnout(
        db,
        request.worker_id,
        request.survey_id
    )


@router.get(
    "/features/{worker_id}",
    status_code=status.HTTP_200_OK,
    summary="Obtener features de burnout",
    description="Solo retorna los features, sin hacer predicción. Útil para debugging.",
)
async def get_burnout_features(
    worker_id,
    db: Session = Depends(get_db),
):
    """
    Endpoint auxiliar para ver features sin predicción.
    """

    return BurnoutService.get_worker_features(
        db,
        worker_id
    )