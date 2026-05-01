from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.question_surveys_service import QuestionSurveyService
from app.schemas.question_surveys_scheme import AssignQuestions, QuestionSurveyResponse, QuestionSurveyBulkCreate, QuestionSurveyCreate, QuestionSurveyUpdate
from uuid import UUID

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
    # Use exclude_unset=True to only update fields that were provided in the request
    question_survey = service.update_question_survey(question_survey_id, payload.model_dump(exclude_unset=True))
    if not question_survey:  # If the question survey wasn't found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question_survey  # Return the updated question survey

@router.delete("/{question_survey_id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE endpoint para quitar una pregunta de una encuesta
def delete_question_survey(question_survey_id: UUID, db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    deleted = service.delete_question_survey(question_survey_id)  # Try to delete
    if not deleted:  # If the question wasn't found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    # No return value needed for 204 No Content

@router.post("/assign", status_code=status.HTTP_200_OK)
def assign_questions_to_survey(payload: AssignQuestions= Depends(AssignQuestions.as_form), db: Session = Depends(get_db)):
    service = QuestionSurveyService(db)
    return service.assign_questions(payload)