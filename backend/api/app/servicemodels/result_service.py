# Servicio para gestionar resultados de encuestas.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Result
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.dbmodels import Group, Worker, Area, Surveys

class ResultService:
    # CRUD para resultados de encuestas con filtrado por rol
    def __init__(self, db: Session):
        self.repo = ur(Result, db)
        self.db = db         

    def get_results(self):
        # Obtener todos los resultados
        return self.repo.get_all()

    def get_result_by_id(self, id: UUID):
        # Obtener resultado por ID
        return self.repo.get_by_id(id)
    
    def get_results_by_worker(self, worker_id: UUID):
        # Obtener resultados de un trabajador (acceso personal)
        return self.db.query(Result).filter(Result.id_worker == worker_id).all()
    
    def get_results_by_group(self, group_id: UUID):
        # Obtener resultados de grupo (líder puede ver)
        return self.db.query(Result).filter(Result.id_group == group_id).all()

    def create_result(self, data: dict):
        # Crear resultado con validaciones de existencia
        group = ur(Group, self.db).get_by_id(data["id_group"])
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El grupo no existe"
            )
        worker = ur(Worker, self.db).get_by_id(data["id_worker"])
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe"
            )
        area = ur(Area, self.db).get_by_id(data["id_area"])
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área no existe"
            )
        surveys = ur(Surveys, self.db).get_by_id(data["id_survey"])
        if not surveys:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe"
            )
        return self.repo.create(data)
    
    def update_result_flag(self, result_id: UUID, flag: bool):
        # Actualizar bandera de resultado (para marcar casos especiales)
        result = self.get_result_by_id(result_id)
        if not result:
            return None
        
        result.flag = flag
        self.db.commit()
        self.db.refresh(result)
        
        return result
