# Servicio para gestionar operaciones de encuestas.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Surveys
from sqlalchemy.orm import Session
from uuid import UUID
from app.dbmodels import Question, QuestionSurveys
from sqlalchemy.orm import joinedload

class SurveyService:
    # Operaciones CR para encuestas (puede incluir D a futuro)
    def __init__(self, db: Session) -> None:
        self.repo = ur(Surveys, db)
    
    def get_surveys(self):
        # Obtener todas las encuestas
        return self.repo.get_all()
    
    def get_survey(self, id: UUID):
        # Obtener encuesta por ID
        return self.repo.get_by_id(id)
    
    def create_survey(self, data: dict):
        # Crear nueva encuesta
        return self.repo.create(data)
    