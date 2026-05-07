# Servicio para gestionar trabajadores.
# Proporciona operaciones CRUD y funciones de negocio relacionadas con trabajadores.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Worker
from sqlalchemy.orm import Session
from uuid import UUID

class WorkerService:
    # Operaciones CR para trabajadores con funciones especializadas
    def __init__(self, db: Session) -> None:
        self.repo = ur(Worker, db)
        self.db = db
    
    def get_workers(self):
        # Obtener todos los trabajadores
        return self.repo.get_all()
    
    def get_worker(self, id: UUID):
        # Obtener trabajador por ID
        return self.repo.get_by_id(id)
    
    def create_worker(self, data: dict):
        # Crear nuevo trabajador
        return self.repo.create(data)
    
    def update_worker_flag(self, worker_id: UUID, flag: bool):
        # Actualizar bandera de trabajador (para marcar casos especiales)
        worker = self.get_worker(worker_id)
        if not worker:
            return None
        
        worker.flag = flag
        self.db.commit()
        self.db.refresh(worker)
        
        return worker
    
    def get_workers_by_group(self, group_id: UUID):
        # Obtener trabajadores de un grupo específico
        return self.db.query(Worker).filter(Worker.id_group == group_id).all()