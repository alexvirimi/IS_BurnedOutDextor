# Módulo de endpoints para gestionar encuestas.
# Solo RRHH puede crear o modificar encuestas.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.surveys_service import SurveyService
from app.schemas.surveys_scheme import (
    SurveyResponse,
    SurveyCreate,
    SurveyUpdate,
    SurveyWithQuestions,
    SurveyComplete,
)
from uuid import UUID
from sqlalchemy.orm import joinedload
from app.dbmodels import Surveys, QuestionSurveys
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.get("/", response_model=list[SurveyResponse])
def read_surveys(db: Session = Depends(get_db)):
    service = SurveyService(db)
    return service.get_surveys()


@router.get("/{survey_id}", response_model=SurveyResponse)
def read_survey(survey_id: UUID, db: Session = Depends(get_db)):
    service = SurveyService(db)
    survey = service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return survey


@router.get("/{survey_id}/questions", response_model=SurveyWithQuestions, status_code=status.HTTP_200_OK)
def read_survey_with_questions(survey_id: UUID, db: Session = Depends(get_db)):
    service = SurveyService(db)
    survey = service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")

    survey_with_questions = db.query(Surveys).options(
        joinedload(Surveys.question_surveys).joinedload(QuestionSurveys.question)
    ).filter(Surveys.id == survey_id).first()

    if not survey_with_questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")

    questions = [qs.question for qs in survey_with_questions.question_surveys]
    return {
        "id": survey_with_questions.id,
        "name": survey_with_questions.name,
        "questions": questions,
    }


@router.get("/{survey_id}/complete", response_model=SurveyComplete, status_code=status.HTTP_200_OK)
def read_survey_complete(survey_id: UUID, db: Session = Depends(get_db)):
    service = SurveyService(db)
    survey_complete = service.get_survey_complete(survey_id, db)
    if not survey_complete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return survey_complete


@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
def create_survey(
    payload: SurveyCreate = Depends(SurveyCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db),
):
    service = SurveyService(db)
    return service.create_survey(payload.model_dump())


@router.patch("/{survey_id}", response_model=SurveyResponse, status_code=status.HTTP_200_OK)
def update_survey(
    survey_id: UUID,
    payload: SurveyUpdate,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db),
):
    """
    Actualización parcial de una encuesta. Solo RRHH.
    Acepta cualquier combinación de: name, aperture_date, finishing_date, status.
    Solo se modifican los campos enviados en el body.
    """
    service = SurveyService(db)
    # exclude_none=True ensures only supplied fields are written
    updated = service.update_survey(survey_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encuesta no encontrada",
        )
    return updated
