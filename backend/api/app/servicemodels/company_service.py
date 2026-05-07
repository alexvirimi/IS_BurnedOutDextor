from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Company
from sqlalchemy.orm import Session 
from uuid import UUID

# En la tabla area solo se pueden realizar las lecturas de la misma + Create.
class CompanyService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(Company, db)             # modelo + sesión
    
    def get_workers_info(self):
        return self.repo.get_all()              # devuelve la información de todos los trabajadores
    
    def get_worker_info(self, id: UUID):
        return self.repo.get_by_id(id)          # devuelve toda la información de un trabajador
    
    def create_worker_info(self, data: dict):
        return self.repo.create(data)           # crea los detalles de un trabajador que se pasan en forma de diccionario