from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.group_scheme import GroupCreate, GroupResponse, GroupAssignLeader, GroupUpdate
from app.dbmodels.groups import Group
from app.database import get_db
from app.dbmodels.workers import Worker
from app.dbmodels.area import Area
router = APIRouter(prefix="/group", tags=["groups"])

@router.post("/", response_model=GroupResponse)
def create_group(group: GroupCreate= Depends (GroupCreate.as_form), db: Session = Depends(get_db)):

    area = db.query(Area).filter(Area.id == group.id_area).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    if group.id_leader:
        worker = db.query(Worker).filter(Worker.id == group.id_leader).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Trabajador lider no encontrado")

    new_group = Group(
        name=group.name,
        id_area=group.id_area,
        id_leader=group.id_leader  
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group

@router.patch("/{group_id}/leader", response_model=GroupResponse)
def assign_leader(group_id: UUID, data: GroupAssignLeader = Depends(GroupAssignLeader.as_form), db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    worker = db.query(Worker).filter(Worker.id == data.id_leader).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Trabajador no encontrado")
    if worker.id_group != group_id:
        raise HTTPException(status_code=400, detail="El trabajador no pertenece a este grupo")
    
    group.id_leader = data.id_leader
    db.commit()
    db.refresh(group)
    return group

@router.get("/", response_model=list[GroupResponse])
def get_groups(db: Session = Depends(get_db)):
    groups = db.query(Group).all()
    return groups

@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: UUID, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return group

