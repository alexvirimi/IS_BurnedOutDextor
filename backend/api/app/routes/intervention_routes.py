from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Query, status 
from sqlalchemy.orm import Session
from app.database import get_db
from app.dbmodels.result import Result
from app.servicemodels.intervention_management_service import InterventionManagementService
from app.schemas.intervention_scheme import (
    InterventionReviewRequest,
    InterventionResponse,
)

router = APIRouter(
    prefix="/interventions",
    tags=["Intervenciones RRHH"],
)

VALID_STATUSES = ["Pendiente", "Aprobada", "Rechazada", "Ejecutada"]


@router.get(
    "/",
    response_model=list[InterventionResponse],
    summary="Listar intervenciones por estado",
)
def list_interventions(
    intervention_status: str = Query(
        "Pendiente",
        enum=VALID_STATUSES,
    ),
    db: Session = Depends(get_db),
):
    return (
        db.query(Result)
        .filter(Result.intervention_status == intervention_status)
        .order_by(Result.generation_date.desc())
        .all()
    )


@router.get("/{result_id}", response_model=InterventionResponse, summary="Detalle de una intervención")
def get_intervention(result_id: UUID, db: Session = Depends(get_db)):
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resultado no encontrado.")
    return result


@router.patch("/{result_id}/review", response_model=InterventionResponse, status_code=status.HTTP_200_OK, summary="Cambiar estado y/o agregar comentario de RRHH")
def review_intervention(
    result_id: UUID,
    intervention_status: str = Form(
        ...,
        description="Estado de la intervención",
        enum=VALID_STATUSES,
    ),
    hr_comment: Optional[str] = Form(
        None,
        max_length=2000,
        description="Comentario de RRHH",
    ),
    db: Session = Depends(get_db),
):
    request = InterventionReviewRequest(
        intervention_status=intervention_status,
        hr_comment=hr_comment,
    )
    return InterventionManagementService.review(db, result_id, request)