from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Rank
from sqlalchemy.orm import Session 
from uuid import UUID

# En la tabla area solo se pueden realizar las lecturas de la misma + Create.
class RankService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(Rank, db)            # modelo + sesión
    
    def get_ranks(self):
        return self.repo.get_all()          # devuelve todos los parametros
    
    def get_rank_by_id(self, id: UUID):
        return self.repo.get_by_id(id)      # busca un rank por su ID
    
    def create_rank(self, data: dict):      # crea un rank
        return self.repo.create(data)
    
    
