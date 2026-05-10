from app.controllers.crud_controller import UniversalRepository as ur
from app.dbmodels import PsicometricVariable
from sqlalchemy.orm import Session
from uuid import UUID

class PsicometricVariableService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(PsicometricVariable, db)
        self.db = db

    def get_psicometric_variables(self):
        return self.repo.get_all()

    def get_psicometric_variable(self, id: UUID):
        return self.repo.get_by_id(id)

