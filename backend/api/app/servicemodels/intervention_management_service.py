import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.dbmodels.result import Result
from app.schemas.intervention_scheme import InterventionReviewRequest

VALID_STATUSES = {"Pendiente", "Aprobada", "Rechazada", "Ejecutada"}

logger = logging.getLogger(__name__)

# Transiciones válidas
VALID_TRANSITIONS = {
    "Pendiente": {"Aprobada", "Rechazada"},
    "Aprobada":  {"Ejecutada"},
}


class InterventionManagementService:

    @staticmethod
    def review(
        db: Session,
        result_id: UUID,
        request: InterventionReviewRequest,
    ) -> Result:
        result = db.query(Result).filter(Result.id == result_id).first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resultado no encontrado.",
            )

        if request.intervention_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Estado inválido. Valores permitidos: {VALID_STATUSES}",
            )

        allowed = VALID_TRANSITIONS.get(result.intervention_status, set())
        if request.intervention_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede pasar de '{result.intervention_status}' "
                f"a '{request.intervention_status}'. "
                f"Transiciones válidas: {allowed or 'ninguna'}.",
            )

        result.intervention_status = request.intervention_status
        if request.hr_comment is not None:
            result.hr_comment = request.hr_comment

        db.commit()
        db.refresh(result)
        logger.info("Resultado %s → %s", result_id,
                    request.intervention_status)
        return result
