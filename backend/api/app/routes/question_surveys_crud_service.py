# Módulo de endpoints para gestionar relaciones pregunta-encuesta.
# Solo RRHH puede crear, actualizar o eliminar estas relaciones.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.question_surveys_service import QuestionSurveyService
from app.schemas.question_surveys_scheme import AssignQuestions, QuestionSurveyResponse, QuestionSurveyBulkCreate, QuestionSurveyCreate, QuestionSurveyUpdate
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/question_survey", tags=["QuestionSurvey"])

@router.get("/", response_model=list[QuestionSurveyResponse])
# Obtiene todas las relaciones pregunta-encuesta.
def read_questions(db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    return service.get_question_surveys()

@router.get("/{question_survey_id}", response_model=QuestionSurveyResponse)
# Obtiene una relación pregunta-encuesta específica.
def read_question(question_survey_id: UUID, db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    question_survey = service.get_question_survey(question_survey_id)
    if not question_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question_survey

@router.post("/", response_model=QuestionSurveyResponse, status_code=status.HTTP_201_CREATED)
# Crea una relación pregunta-encuesta. Solo RRHH.
def create_question(
    payload: QuestionSurveyCreate = Depends(QuestionSurveyCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = QuestionSurveyService(db)
    return service.create_question_survey(payload.model_dump())

@router.put("/{question_survey_id}", response_model=QuestionSurveyResponse)
# Actualiza una relación pregunta-encuesta. Solo RRHH.
def update_question_survey(
    question_survey_id: UUID,
    payload: QuestionSurveyUpdate = Depends(QuestionSurveyUpdate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = QuestionSurveyService(db)
    # Use exclude_unset=True para actualizar solo campos modificados
    question_survey = service.update_question_survey(question_survey_id, payload.model_dump(exclude_unset=True))
    if not question_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question_survey

@router.delete("/{question_survey_id}", status_code=status.HTTP_204_NO_CONTENT)
# Elimina una relación pregunta-encuesta. Solo RRHH.
def delete_question_survey(
    question_survey_id: UUID,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = QuestionSurveyService(db)
    deleted = service.delete_question_survey(question_survey_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")

@router.post("/assign")
# Asigna múltiples preguntas a una encuesta. Solo RRHH.
def assign_questions(
    payload: AssignQuestions = Depends(AssignQuestions.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = QuestionSurveyService(db)
    return service.assign_questions(payload)