from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.company_service import CompanyService
from app.schemas.company_scheme import CompanyResponse, CompanyCreate
from uuid import UUID

router = APIRouter(prefix="/company", tags=["Company"])

@router.get("/", response_model=list[CompanyResponse])                                                   # obtiene la información de todos los trabajadores
def read_workers_info(db: Session = Depends(get_db)):
    service = CompanyService(db)
    return service.get_workers_info()

@router.get("/{worker_info_id}", response_model=CompanyResponse)                                                   # obtiene todos los detalles de un trabajador dada la id de sus detalles
def read_worker_info(worker_info_id: UUID, db: Session = Depends(get_db)):
    service = CompanyService(db)
    company = service.get_worker_info(worker_info_id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detalles de trabajador no encontrados")
    return company

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)                              # crea los detalles de un trabajador dado un diccionario
def create_worker_info(payload: CompanyCreate = Depends(CompanyCreate.as_form), db: Session = Depends(get_db)):
    service = CompanyService(db)
    return service.create_worker_info(payload.model_dump())