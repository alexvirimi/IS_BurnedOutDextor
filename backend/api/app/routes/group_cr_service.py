from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.servicemodels.group_service import GroupService
from app.schemas.group_scheme import GroupResponse, GroupCreate
from uuid import UUID

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.get("/", response_model=list[GroupResponse]) #Endpoint que recibe en .JSON todas las groups usando la conexion con el servicio dispuesto
def read_groups(db: Session = Depends(get_db)):
    service = GroupService(db)
    return service.get_groups()

@router.get("/{group_id}", response_model=GroupResponse) #Endpoint que recibe un group especifica usando su universal unique identifier (UUID) y la trae a su swagger
def read_group(group_id: UUID, db: Session = Depends(get_db)):
    service = GroupService(db)
    group = service.get_group_by_id(group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo no encontrado")
    return group

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)#Endpoint que crea un group
def create_group(payload: GroupCreate, db: Session = Depends(get_db)):
    service = GroupService(db)
    return service.create_group(payload.model_dump())

#@router.get("/{leader_id}/workers", response_model=list[WorkerResponse])
#def read_workers_by_leader(leader_id: UUID, db: Session = Depends(get_db)):
    service = GroupService(db)
    workers = service.get_workers_by_leader(leader_id)
    if not workers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron workers para ese líder"
        )
    return workers