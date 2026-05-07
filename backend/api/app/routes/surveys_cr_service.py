# Módulo de endpoints para gestionar encuestas.
# Solo RRHH puede crear nuevas encuestas.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.surveys_service import SurveyService
from app.schemas.surveys_scheme import SurveyResponse, SurveyCreate, SurveyWithQuestions
from uuid import UUID
from sqlalchemy.orm import joinedload
from app.dbmodels import Surveys, QuestionSurveys
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData

router = APIRouter(prefix="/survey", tags=["Survey"])

@router.get("/", response_model=list[SurveyResponse])
# Obtiene todas las encuestas creadas.
def read_surveys(db: Session = Depends(get_db)):
    service = SurveyService(db)
    return service.get_surveys()

@router.get("/{survey_id}", response_model=SurveyResponse)
# Obtiene la información de una encuesta dada su UUID.
def read_survey(survey_id: UUID, db: Session = Depends(get_db)):
    service = SurveyService(db)
    survey = service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return survey

@router.get("/{survey_id}/questions", response_model=SurveyWithQuestions, status_code=status.HTTP_200_OK)
# Obtiene encuesta con sus preguntas asociadas.
def read_survey_with_questions(survey_id: UUID, db: Session = Depends(get_db)):
    service = SurveyService(db)
    survey = service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    
    # Cargar preguntas con joinedload para evitar consultas adicionales
    survey_with_questions = db.query(Surveys).options(
        joinedload(Surveys.question_surveys).joinedload(QuestionSurveys.question)
    ).filter(Surveys.id == survey_id).first()
    
    if not survey_with_questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    
    # Mapear a estructura esperada
    questions = [qs.question for qs in survey_with_questions.question_surveys]
    result = {
        "id": survey_with_questions.id,
        "name": survey_with_questions.name,
        "questions": questions
    }
    return result

@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
# Crea una encuesta. Solo RRHH.
def create_survey(
    payload: SurveyCreate = Depends(SurveyCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = SurveyService(db)
    return service.create_survey(payload.model_dump())
