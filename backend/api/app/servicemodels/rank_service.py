# Servicio para gestionar rangos y niveles de autorización.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Rank
from sqlalchemy.orm import Session
from uuid import UUID

class RankService:
    # Operaciones CR para rangos (Create + Read)
    def __init__(self, db: Session) -> None:
        self.repo = ur(Rank, db)
    
    def get_ranks(self):
        # Obtener todos los rangos
        return self.repo.get_all()
    
    def get_rank_by_id(self, id: UUID):
        # Obtener rango por ID
        return self.repo.get_by_id(id)
    
    def create_rank(self, data: dict):
        # Crear nuevo rango
        return self.repo.create(data)
