# Endpoints para gestionar trabajadores.
# Solo RRHH (nivel 3) puede crear o modificar trabajadores.
# Los líderes pueden actualizar el flag. RRHH NO puede.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.workers_service import WorkerService
from app.schemas.workers_scheme import WorkerResponse, WorkerCreate, WorkerDetailResponse
from app.deps.auth_deps import get_current_user, require_rrhh
from app.schemas.auth_scheme import CurrentUserData
from pydantic import BaseModel
from uuid import UUID

router = APIRouter(prefix="/worker", tags=["Worker"])


class UpdateWorkerFlagRequest(BaseModel):
    flag: bool


@router.get("/", response_model=list[WorkerResponse], status_code=status.HTTP_200_OK)
def read_workers(db: Session = Depends(get_db)):
    service = WorkerService(db)
    return service.get_workers()


@router.get("/{worker_id}/details", response_model=WorkerDetailResponse, status_code=status.HTTP_200_OK)
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
        "group": worker.group.name if worker.group else None,
    }


@router.get("/{worker_id}", response_model=WorkerResponse, status_code=status.HTTP_200_OK)
def read_worker_info(worker_id: UUID, db: Session = Depends(get_db)):
    service = WorkerService(db)
    worker = service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado")
    return worker


@router.post("/", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def create_worker(
    payload: WorkerCreate = Depends(WorkerCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db),
):
    service = WorkerService(db)
    return service.create_worker(payload.model_dump())


@router.patch("/{worker_id}/flag", response_model=WorkerResponse, status_code=status.HTTP_200_OK)
def update_worker_flag(
    worker_id: UUID,
    payload: UpdateWorkerFlagRequest,
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Solo líderes (nivel 2) pueden cambiar el flag. RRHH NO puede.
    if current_user.rank_level == 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El personal de RRHH no puede modificar el flag de trabajadores",
        )
    if current_user.rank_level != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar el flag de trabajadores",
        )

    service = WorkerService(db)
    worker = service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado")

    worker.flag = payload.flag
    db.commit()
    db.refresh(worker)
    return worker
