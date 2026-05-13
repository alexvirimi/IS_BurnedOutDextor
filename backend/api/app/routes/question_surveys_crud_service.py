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
from app.exceptions import BusinessValidationError

router = APIRouter(prefix="/question_survey", tags=["QuestionSurvey"])

@router.get("/", response_model=list[QuestionSurveyResponse], status_code=status.HTTP_200_OK)
def read_question_surveys(db: Session = Depends(get_db)):                                                                   # endpoint que devuelve todas las preguntas creadas
    service = QuestionSurveyService(db)
    return service.get_question_surveys()

@router.get("/{question_survey_id}", response_model=QuestionSurveyResponse, status_code=status.HTTP_200_OK)                                                   # endpoint que obtiene la información de una pregunta dada su UUID
def read_question_survey(question_survey_id: UUID, db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    question_survey = service.get_question_survey(question_survey_id)
    if not question_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question_survey


@router.post("/", response_model=QuestionSurveyResponse, status_code=status.HTTP_201_CREATED)                              # endpoint que crea una pregunta dado un diccionario con sus parámetros
def create_question_survey(payload: QuestionSurveyCreate = Depends(QuestionSurveyCreate.as_form), db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    return service.create_question_survey(payload.model_dump())

@router.put("/{question_survey_id}", response_model=QuestionSurveyResponse, status_code=status.HTTP_200_OK)  # Confieso mis pecados ante Cristo. Endpoint que actualiza una pregunta
def update_question_survey(question_survey_id: UUID, payload: QuestionSurveyUpdate = Depends(QuestionSurveyUpdate.as_form), db: Session = Depends(get_db)):
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

@router.post("/assign", status_code=status.HTTP_200_OK)
def assign_questions_to_survey(payload: AssignQuestions, db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    try:
        return service.assign_questions(payload)
    except BusinessValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))