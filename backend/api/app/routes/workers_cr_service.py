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
from pydantic import BaseModel

router = APIRouter(prefix="/worker", tags=["Worker"])

class UpdateFlagRequest(BaseModel):
    # Esquema para actualizar el flag de un trabajador.
    flag: bool

@router.get("/", response_model=list[WorkerResponse], status_code=status.HTTP_200_OK)
def read_workers(db: Session = Depends(get_db)):
    # Endpoint para obtener todos los trabajadores. No requiere autenticación.
    service = WorkerService(db)
    return service.get_workers()

@router.get("/{worker_id}", response_model=WorkerResponse, status_code=status.HTTP_200_OK)
def read_worker_info(worker_id: UUID, db: Session = Depends(get_db)):
    # Endpoint que obtiene la información de un trabajador dada su UUID. No requiere autenticación.
    service = WorkerService(db)
    worker = service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado")
    return worker

@router.post("/", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def create_worker_info(
    payload: WorkerCreate = Depends(WorkerCreate.as_form),
    current_user: CurrentUserData = Depends(require_rrhh),
    db: Session = Depends(get_db)
):
    # Endpoint que crea un trabajador. Solo RRHH puede crear trabajadores.
    service = WorkerService(db)
    return service.create_worker(payload.model_dump())

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

@router.patch("/{worker_id}/flag", response_model=WorkerResponse, status_code=status.HTTP_200_OK)
def update_worker_flag(
    worker_id: UUID,
    payload: UpdateFlagRequest,
    current_user: CurrentUserData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Endpoint para actualizar el flag de un trabajador.
    # Restricciones: Nivel 2 (líder) solo de su grupo, Nivel 3 (RRHH) NO puede.
    service = WorkerService(db)
    
    # Valida que el usuario tenga permiso para actualizar el flag
    if current_user.rank_level == 3:
        # RRHH NO puede modificar el flag
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El personal de RRHH no puede modificar el flag de trabajadores"
        )
    elif current_user.rank_level != 2:
        # Solo nivel 2 (líderes) pueden modificar el flag
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar el flag de trabajadores. Solo líderes pueden hacer esto."
        )
    
    # Obtiene el trabajador a actualizar
    worker = service.get_worker(worker_id)
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajador no encontrado")
    
    # Valida que el líder solo puede actualizar el flag de trabajadores de su grupo
    if worker.id_group != current_user.id_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes actualizar el flag de trabajadores de tu grupo"
        )
    
    # Actualiza el flag
    updated_worker = service.update_worker_flag(worker_id, payload.flag)
    return updated_worker