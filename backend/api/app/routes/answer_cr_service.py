# Módulo de endpoints para gestionar respuestas a preguntas.
# Cualquier usuario autenticado puede responder preguntas.
# Solo RRHH puede crear respuestas manualmente para otros usuarios.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.answer_service import AnswerService
from app.schemas.answer_scheme import AnswerResponse, AnswerCreate, AnswerUserCreate, BulkAnswerCreate
from app.servicemodels.survey_assignment_service import SurveyAssignmentService
from app.deps.auth_deps import require_rrhh, get_current_user, require_any_authenticated
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

@router.get("/my/all", response_model=list[AnswerResponse])
# Obtiene todas las respuestas del usuario actual
def read_my_answers(
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AnswerService(db)
    answers = service.get_answers_by_worker(current_user.worker_id)
    if not answers:
        return []
    return answers

@router.post("/respond", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
# Crea una nueva respuesta. Cualquier usuario autenticado puede responder.
# Obtiene automáticamente: id_worker, id_group, id_area del usuario logueado.
def respond_to_question(
    payload: AnswerUserCreate = Depends(AnswerUserCreate.as_form),
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint público para que usuarios respondan preguntas de encuestas.
    
    Solo requiere:
    - id_question_survey: UUID de la pregunta en la encuesta
    - value: Valor de la respuesta (1-5)
    
    El sistema obtiene automáticamente:
    - El worker_id del usuario logueado
    - El id_group del worker
    - El id_area del grupo del worker
    """
    service = AnswerService(db)
    return service.create_answer_from_user(
        worker_id=current_user.worker_id,
        question_survey_id=payload.id_question_survey,
        value=payload.value
    )

@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
# Crea una nueva respuesta manualmente. Solo RRHH.
# Usado por RRHH si necesita registrar respuestas para otros usuarios.
def create_answer(
    payload: AnswerCreate = Depends(AnswerCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    """
    Endpoint para RRHH creando respuestas manualmente.
    Requiere todos los parámetros incluyendo id_worker, id_group, id_area.
    """
    service = AnswerService(db)
    return service.create_answer(payload.model_dump())

@router.post("/bulk", response_model=list[AnswerResponse], status_code=status.HTTP_201_CREATED)
# Crea múltiples respuestas de una encuesta de una vez. Cualquier usuario autenticado.
def create_bulk_answers(
    payload: BulkAnswerCreate,
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
   
    assignment_service = SurveyAssignmentService(db)
    
    can_respond = assignment_service.can_worker_respond_survey(
        current_user.worker_id,
        payload.id_survey
    )
    
    if not can_respond:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta encuesta no te fue asignada. No puedes responderla."
        )
    

    service = AnswerService(db)
    
    # Convertir BulkAnswerItem a diccionarios para el servicio
    answers_data = [{"id_question_survey": a.id_question_survey, "value": a.value} for a in payload.answers]
    
    return service.create_bulk_answers(
        worker_id=current_user.worker_id,
        survey_id=payload.id_survey,
        answers_data=answers_data
    )

