from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Worker
from sqlalchemy.orm import Session 
from uuid import UUID

# C + R básico
class WorkerService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(Worker, db)              # modelo + sesión
    
    def get_worker(self, id: UUID):
        return self.repo.get_by_id(id)          # busca la información básica de un trabajador dado su UUID
    
    def create_worker(self, data: dict):
        return self.repo.create(data)           # crea un trabajador con su información básica dado un diccionario