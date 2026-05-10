# Servicio para gestionar información empresarial de trabajadores.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Company
from sqlalchemy.orm import Session
from uuid import UUID

class CompanyService:
    # Operaciones CRUD para información de empleados
    def __init__(self, db: Session) -> None:
        self.repo = ur(Company, db)
    
    def get_workers_info(self):
        # Obtener información de todos los trabajadores
        return self.repo.get_all()
    
    def get_worker_info(self, id: UUID):
        return self.repo.get_by_worker_or_company_id(id)
    
    def create_worker_info(self, data: dict):
        # Crear información de trabajador
        return self.repo.create(data)