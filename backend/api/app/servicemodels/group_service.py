# Servicio para gestionar operaciones de grupos.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Result
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.dbmodels import Group, Worker, Area, Surveys

class GroupService:
    # Operaciones CRUD para grupos
    def __init__(self, db: Session):
        self.repo = ur(Group, db)
        self.db = db         
        
    def get_workers_by_leader(self, leader_id: UUID):
        # Obtener trabajadores supervisados por un líder
        return (
            self.db.query(Worker)
            .join(Group, Worker.id_group == Group.id)
            .filter(Group.id_leader == leader_id)
            .all()
        )
        
    def get_groups(self):
        # Obtener todos los grupos
        return self.repo.get_all()

    def get_group_by_id(self, id: UUID):
        # Obtener grupo por ID
        return self.repo.get_by_id(id)
    
    def create_group(self, data: dict):
        # Crear nuevo grupo con validaciones
        if data.get("id_leader"):
            leader = ur(Worker, self.db).get_by_id(data["id_leader"])
            if not leader:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="El worker líder no existe"
                )

        area = ur(Area, self.db).get_by_id(data["id_area"])
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área no existe"
            )

        surveys = ur(Surveys, self.db).get_by_id(data["id_surveys"])
        if not surveys:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe"
            )

        return self.repo.create(data)
