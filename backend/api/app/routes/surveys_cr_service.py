from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.surveys_service import SurveyService
from app.schemas.surveys_scheme import SurveyResponse, SurveyCreate, SurveyWithQuestions
from uuid import UUID

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

@router.post("/", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED) # endpoint que crea una encuesta dado un diccionario con sus parámetros
def create_survey(payload: SurveyCreate, db: Session = Depends(get_db)):
    service = SurveyService(db)
    return service.create_survey(payload.model_dump())

@router.get("/{survey_id}/questions", response_model=SurveyWithQuestions) # endpoint que obtiene la información de una encuesta dada su UUID, pero con sus preguntas asociadas
def read_survey_with_questions(survey_id: UUID, db: Session = Depends(get_db)):
    survey = SurveyService(db).get_survey_with_questions(survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encuesta no encontrada")
    return survey