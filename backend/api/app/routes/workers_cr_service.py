# Este módulo define los endpoints para gestionar trabajadores en el sistema.
# Proporciona endpoints para crear, consultar y actualizar información de trabajadores.
# Solo RRHH (nivel 3) puede crear o modificar trabajadores.
# Los endpoints de lectura son accesibles sin autenticación.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.workers_service import WorkerService
from app.schemas.workers_scheme import WorkerResponse, WorkerCreate, WorkerDetailResponse
from app.deps.auth_deps import get_current_user, require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from uuid import UUID

router = APIRouter(prefix="/worker", tags=["Worker"])

@router.get("/", response_model=list[WorkerResponse], status_code=status.HTTP_200_OK)
def read_workers(db: Session = Depends(get_db)):
    # Endpoint para obtener todos los trabajadores. No requiere autenticación.
    service = WorkerService(db)
    return service.get_workers()
@router.get("/{worker_id}/details", response_model=WorkerDetailResponse, status_code=status.HTTP_200_OK)
def read_worker_details(worker_id: UUID, db: Session = Depends(get_db)):
    # Endpoint que obtiene toda la información de un trabajador incluyendo rango y grupo. No requiere autenticación.
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
        "flag": worker.flag,
        "id_rank": worker.id_rank,
        "id_group": worker.id_group,
        "rank": worker.rank.rank_name if worker.rank else None,
        "group": worker.group.name if worker.group else None
    }

@router.get("/{worker_id}", response_model=WorkerResponse, status_code=status.HTTP_200_OK)
def read_worker_info(worker_id: UUID, db: Session = Depends(get_db)):
    # Endpoint que obtiene la información de un trabajador dada su UUID. No requiere autenticación.
    service = WorkerService(db)
    worker = service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado")
    return worker