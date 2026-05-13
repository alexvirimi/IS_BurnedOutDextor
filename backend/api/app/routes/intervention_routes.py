from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.intervention_management_service import InterventionManagementService
from app.schemas.intervention_scheme import (
    InterventionReviewRequest,
    InterventionResponse,
)
from app.dbmodels.result import Result

router = APIRouter(
    prefix="/interventions",
    tags=["Intervenciones RRHH"],
)


@router.patch("/{result_id}/review", response_model=InterventionResponse, status_code=status.HTTP_200_OK, summary="Cambiar estado y/o agregar comentario de RRHH")
def review_intervention(
    result_id: UUID,
    request: InterventionReviewRequest,
    db: Session = Depends(get_db),
):
    return InterventionManagementService.review(db, result_id, request)

@router.get("/", response_model=list[InterventionResponse], summary="Listar intervenciones por estado",)
def list_interventions(intervention_status: str = "Pendiente", db: Session = Depends(get_db)):
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
