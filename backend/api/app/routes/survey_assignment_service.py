# Endpoints para gestionar asignaciones de encuestas a trabajadores
# Solo RRHH puede asignar encuestas
# Workers pueden ver sus encuestas asignadas

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.survey_assignment_service import SurveyAssignmentService
from app.schemas.survey_assignment_scheme import (
    AssignSurveyToWorkers,
    SurveyWorkerAssignmentResponse,
    MySurveyResponse,
    BulkAssignSurveyToWorkers
)
from app.deps.auth_deps import require_rrhh, get_current_user
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/survey-assignment", tags=["Survey Assignment"])


@router.post("/assign", response_model=list[SurveyWorkerAssignmentResponse], status_code=status.HTTP_201_CREATED)
def assign_survey_to_workers(
    payload: AssignSurveyToWorkers,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = SurveyAssignmentService(db)
    return service.assign_survey_to_workers(payload.id_survey, payload.worker_ids)


@router.post("/assign-bulk", response_model=list[SurveyWorkerAssignmentResponse], status_code=status.HTTP_201_CREATED)
def assign_surveys_bulk(
    payload: BulkAssignSurveyToWorkers,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):

    service = SurveyAssignmentService(db)
    return service.assign_survey_to_workers_bulk(payload.survey_ids, payload.worker_ids)


@router.get("/survey/{survey_id}/assignments", response_model=list[dict], status_code=status.HTTP_200_OK)
def get_survey_assignments(
    survey_id: UUID,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):

    service = SurveyAssignmentService(db)
    return service.get_survey_assignments(survey_id)


@router.get("/worker/{worker_id}/assignments", response_model=list[dict], status_code=status.HTTP_200_OK)
def get_worker_assignments(
    worker_id: UUID,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las encuestas asignadas a un trabajador.
    Solo RRHH.
    """
    service = SurveyAssignmentService(db)
    return service.get_worker_assignments(worker_id)


@router.get("/my-surveys", response_model=list[MySurveyResponse], status_code=status.HTTP_200_OK)
def get_my_surveys(
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    service = SurveyAssignmentService(db)
    return service.get_my_surveys(current_user.worker_id)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_assignment(
    assignment_id: UUID,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):

    service = SurveyAssignmentService(db)
    service.remove_assignment(assignment_id)
