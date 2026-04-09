from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.result_service import ResultService
from app.schemas.result_scheme import ResultResponse, ResultCreate
from uuid import UUID

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/", response_model=list[ResultResponse]) #Endpoint que recibe en .JSON todas las results usando la conexion con el servicio dispuesto
def read_results(db: Session = Depends(get_db)):
    service = ResultService(db)
    return service.get_results()

@router.get("/{result_id}", response_model=ResultResponse) #Endpoint que recibe un result especifica usando su universal unique identifier (UUID) y la trae a su swagger
def read_result(result_id: UUID, db: Session = Depends(get_db)):
    service = ResultService(db)
    result = service.get_result_by_id(result_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resultado no encontrado")
    return result

@router.post("/", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)#Endpoint que crea un result
def create_result(payload: ResultCreate, db: Session = Depends(get_db)):
    service = ResultService(db)
    return service.create_result(payload.model_dump())