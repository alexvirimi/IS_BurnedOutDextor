# Módulo de endpoints para gestionar respuestas a preguntas.
# Solo RRHH puede crear nuevas respuestas.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.answer_service import AnswerService
from app.schemas.answer_scheme import AnswerResponse, AnswerCreate
from app.deps.auth_deps import require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/answers", tags=["Answers"])

@router.get("/", response_model=list[AnswerResponse])
# Obtiene todas las respuestas disponibles.
def read_answers(db: Session = Depends(get_db)):
    service = AnswerService(db)
    return service.get_answers()

@router.get("/{answer_id}", response_model=AnswerResponse)
# Obtiene una respuesta específica dada su UUID.
def read_answer(answer_id: UUID, db: Session = Depends(get_db)):
    service = AnswerService(db)
    answer = service.get_answer_by_id(answer_id)
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Respuesta no encontrada")
    return answer

@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
# Crea una nueva respuesta. Solo RRHH.
def create_answer(
    payload: AnswerCreate = Depends(AnswerCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    service = AnswerService(db)
    return service.create_answer(payload.model_dump())

