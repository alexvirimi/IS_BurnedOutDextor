from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.question_surveys_service import QuestionSurveyService
from app.schemas.question_surveys_scheme import QuestionSurveyResponse, QuestionSurveyCreate
from uuid import UUID

router = APIRouter(prefix="/question_survey", tags=["QuestionSurvey"])

@router.get("/", response_model=list[QuestionSurveyResponse])
def read_questions(db: Session = Depends(get_db)):                                                                   # endpoint que devuelve todas las preguntas creadas
    service = QuestionSurveyService(db)
    return service.get_question_surveys()

@router.get("/{question_survey_id}", response_model=QuestionSurveyResponse)                                                   # endpoint que obtiene la información de una pregunta dada su UUID
def read_question(question_survey_id: UUID, db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    question_survey = service.get_question_survey(question_survey_id)
    if not question_survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question_survey


@router.post("/", response_model=QuestionSurveyResponse, status_code=status.HTTP_201_CREATED)                              # endpoint que crea una pregunta dado un diccionario con sus parámetros
def create_question(payload: QuestionSurveyCreate, db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    return service.create_question_survey(payload.model_dump())
