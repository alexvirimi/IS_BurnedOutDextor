from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.surveys_service import SurveyService
from app.schemas.surveys_scheme import SurveyResponse, SurveyCreate, SurveyWithQuestions
from uuid import UUID
from sqlalchemy.orm import joinedload
from app.dbmodels import Surveys, QuestionSurveys
from app.deps.auth_deps import require_rrhh  # Importación añadida
from app.schemas.auth_scheme import CurrentUserData # Importación añadida

router = APIRouter(prefix="/survey", tags=["Survey"])

@router.get("/", response_model=list[SurveyResponse])
def read_surveys(db: Session = Depends(get_db)):  # endpoint que devuelve todas las encuestas creadas
    service = SurveyService(db)
    return service.get_surveys()

@router.get("/{survey_id}", response_model=SurveyResponse)   # endpoint que obtiene la información de una encuesta dada su UUID
def read_survey(survey_id: UUID, db: Session = Depends(get_db)):
    service = SurveyService(db)
    survey = service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return survey

@router.get("/{survey_id}/questions", response_model=SurveyWithQuestions, status_code=status.HTTP_200_OK)   # endpoint que obtiene la información de una encuesta dada su UUID, junto con las preguntas asociadas a esa encuesta
def read_survey_with_questions(survey_id: UUID, db: Session = Depends(get_db)):
    service = SurveyService(db)
    survey = service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    
    # Cargar las preguntas asociadas a la encuesta utilizando joinedload para evitar consultas adicionales
    survey_with_questions = db.query(Surveys).options(
        joinedload(Surveys.question_surveys).joinedload(QuestionSurveys.question)
    ).filter(Surveys.id == survey_id).first()
    
    if not survey_with_questions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    
    # Mapear la estructura de question_surveys a la estructura esperada por SurveyWithQuestions
    
    questions = [qs.question for qs in survey_with_questions.question_surveys]
    result = {
        "id": survey_with_questions.id,
        "name": survey_with_questions.name,
        "questions": questions
    }
    return result
    # Yo me arrepentiré de mis pecados después, pero todo sea por hacerle el trabajo más fácil a Alex <3
    # De nada Alex

@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED) # endpoint que crea una encuesta dado un diccionario con sus parámetros
def create_survey(
    payload: SurveyCreate = Depends(SurveyCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh), # Dependencia de autenticación añadida
    db: Session = Depends(get_db)
):
    service = SurveyService(db)
    return service.create_survey(payload.model_dump())
