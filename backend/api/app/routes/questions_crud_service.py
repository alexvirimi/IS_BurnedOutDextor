from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.questions_service import QuestionService
from app.schemas.questions_scheme import QuestionResponse, QuestionCreate
from uuid import UUID

router = APIRouter(prefix="/question", tags=["Question"])

@router.get("/", response_model=list[QuestionResponse])
def read_questions(db: Session = Depends(get_db)):                                                                   # endpoint que devuelve todas las preguntas creadas
    service = QuestionService(db)
    return service.get_questions()

@router.get("/{question_id}", response_model=QuestionResponse)                                                   # endpoint que obtiene la información de una pregunta dada su UUID
def read_question(question_id: UUID, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)                              # endpoint que crea una pregunta dado un diccionario con sus parámetros
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    service = QuestionService(db)
    return service.create_question(payload.model_dump())