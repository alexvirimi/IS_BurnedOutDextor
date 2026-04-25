from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.questions_service import QuestionService
from app.schemas.questions_scheme import QuestionResponse, QuestionCreate, QuestionUpdate
from uuid import UUID

router = APIRouter(prefix="/question", tags=["Question"])

@router.get("/", response_model=list[QuestionResponse], status_code=status.HTTP_200_OK)  # endpoint que devuelve todas las preguntas creadas
def read_questions(db: Session = Depends(get_db)):                                                                   # endpoint que devuelve todas las preguntas creadas
    service = QuestionService(db)
    return service.get_questions()

@router.get("/{question_id}", response_model=QuestionResponse, status_code=status.HTTP_200_OK)                                                   # endpoint que obtiene la información de una pregunta dada su UUID
def read_question(question_id: UUID, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)                              # endpoint que crea una pregunta dado un diccionario con sus parámetros
def create_question(payload: QuestionCreate = Depends(QuestionCreate.as_form), db: Session = Depends(get_db)):
    service = QuestionService(db)
    return service.create_question(payload.model_dump())

@router.put("/{question_id}", response_model=QuestionResponse, status_code=status.HTTP_200_OK)  # Confieso mis pecados ante Cristo. Endpoint que actualiza una pregunta
def update_question(question_id: UUID, payload: QuestionUpdate = Depends(QuestionUpdate.as_form), db: Session = Depends(get_db)):
    service = QuestionService(db)
    # Use exclude_unset=True to only update fields that were provided in the request
    question = service.update_question(question_id, payload.model_dump(exclude_unset=True))
    if not question:  # If the question wasn't found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question  # Return the updated question

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)  # DELETE endpoint for removing a question
def delete_question(question_id: UUID, db: Session = Depends(get_db)):
    service = QuestionService(db)
    deleted = service.delete_question(question_id)  # Try to delete
    if not deleted:  # If the question wasn't found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    # No return value needed for 204 No Content
