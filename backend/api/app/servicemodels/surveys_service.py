from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Surveys
from sqlalchemy.orm import Session 
from uuid import UUID
from app.dbmodels import Question, QuestionSurveys
from sqlalchemy.orm import joinedload
from app.dbmodels import Surveys
# C + R, puede que D a futuro. #Nani?!
class SurveyService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(Surveys, db)             # modelo + sesión
    
    def get_surveys(self):
        return self.repo.get_all()              # obtiene todas las encuestas creadas
    
    def get_survey(self, id: UUID):
        return self.repo.get_by_id(id)          # obtiene todos los detalles de una encuesta dada su ID
    
    def create_survey(self, data: dict):        # crea una encuesta dado un diccionario que contenga todos sus parametros
        return self.repo.create(data)
    