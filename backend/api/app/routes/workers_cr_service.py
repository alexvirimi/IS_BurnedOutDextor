from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.workers_service import WorkerService
from app.schemas.workers_scheme import WorkerResponse, WorkerCreate, WorkerDetailResponse
from uuid import UUID

router = APIRouter(prefix="/worker", tags=["Worker"])

@router.get("/{worker_id}", response_model=WorkerResponse)                                                   # endpoint que obtiene la información de un trabajador dada su UUID
def read_worker_info(worker_id: UUID, db: Session = Depends(get_db)):
    service = WorkerService(db)
    worker = service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado")
    return worker

@router.post("/", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)                              # endpoint que crea los detalles de un trabajador dado un diccionario
def create_worker_info(payload: WorkerCreate, db: Session = Depends(get_db)):
    service = WorkerService(db)
    return service.create_worker(payload.model_dump())

@router.get("/{worker_id}/details", response_model=WorkerDetailResponse)
def read_worker_details(worker_id: UUID, db: Session = Depends(get_db)):
    service = WorkerService(db)
    worker = service.get_worker(worker_id)

    if not worker:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    return {
        "id": worker.id,
        "name": worker.name,
        "last_names": worker.last_names,
        "age": worker.age,
        "gender": worker.gender,
        "id_rank": worker.id_rank,
        "id_group": worker.id_group,
        "rank": worker.rank.rank_name if worker.rank else None,
        "group": worker.group.name if worker.group else None
    }