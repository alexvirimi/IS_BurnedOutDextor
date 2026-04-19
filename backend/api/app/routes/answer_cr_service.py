from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.answer_service import AnswerService
from app.schemas.answer_scheme import AnswerResponse, AnswerCreate, AnswerBulkCreate
from uuid import UUID

router = APIRouter(prefix="/answers", tags=["Answers"])

@router.get("/", response_model=list[AnswerResponse]) #Endpoint que recibe en .JSON todas las answers usando la conexion con el servicio dispuesto
def read_answers(db: Session = Depends(get_db)):
    service = AnswerService(db)
    return service.get_answers()

@router.get("/{answer_id}", response_model=AnswerResponse) #Endpoint que recibe un answer especifica usando su universal unique identifier (UUID) y la trae a su swagger
def read_answer(answer_id: UUID, db: Session = Depends(get_db)):
    service = AnswerService(db)
    answer = service.get_answer_by_id(answer_id)
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Respuesta no encontrada")
    return answer

@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)#Endpoint que crea un answer
def create_answer(payload: AnswerCreate, db: Session = Depends(get_db)):
    service = AnswerService(db)
    return service.create_answer(payload.model_dump())

@router.post("/bulk", response_model=list[AnswerResponse], status_code=status.HTTP_201_CREATED)
def create_answers_bulk(payload: AnswerBulkCreate, db: Session = Depends(get_db)):
    service = AnswerService(db)
    return service.create_answers_bulk(payload.answers)
