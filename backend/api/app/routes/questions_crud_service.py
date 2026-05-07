# Módulo de endpoints para gestionar preguntas de encuestas.
# Solo RRHH puede crear, actualizar o eliminar preguntas.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.questions_service import QuestionService
from app.schemas.questions_scheme import QuestionResponse, QuestionCreate, QuestionUpdate
from app.schemas.surveys_scheme import SurveyResponse
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/question", tags=["Question"])

@router.get("/", response_model=list[QuestionResponse], status_code=status.HTTP_200_OK)
# Obtiene todas las preguntas creadas.
def read_questions(db: Session = Depends(get_db)):
    service = QuestionService(db)
    return service.get_questions()

@router.get("/{question_id}", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
# Obtiene la información de una pregunta dada su UUID.
def read_question(question_id: UUID, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question

@router.get("/{question_id}/surveys", response_model=list[SurveyResponse], status_code=status.HTTP_200_OK)
# Obtiene todas las encuestas relacionadas a una pregunta.
def get_surveys_by_question(question_id: UUID, db: Session = Depends(get_db)):
    service = QuestionService(db)
    # Verificar que la pregunta existe
    question = service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    # Obtener las encuestas relacionadas
    surveys = service.get_surveys_by_question(question_id)
    return surveys

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
# Crea una pregunta. Solo RRHH.
def create_question(
    payload: QuestionCreate = Depends(QuestionCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = QuestionService(db)
    return service.create_question(payload.model_dump())

@router.put("/{question_id}", response_model=QuestionResponse, status_code=status.HTTP_200_OK)
# Actualiza una pregunta. Solo RRHH.
def update_question(
    question_id: UUID,
    payload: QuestionUpdate = Depends(QuestionUpdate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = QuestionService(db)
    # Use exclude_unset=True to only update fields that were provided in the request
    question = service.update_question(question_id, payload.model_dump(exclude_unset=True))
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
    return question

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
# Elimina una pregunta. Solo RRHH.
def delete_question(
    question_id: UUID,
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = QuestionService(db)
    deleted = service.delete_question(question_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada")
