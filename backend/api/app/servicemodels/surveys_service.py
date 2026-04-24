from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Surveys
from sqlalchemy.orm import Session 
from uuid import UUID

# from backend.api.app.dbmodels import questions

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
    
    def get_survey_with_questions(self, survey_id: UUID): # obtiene una encuesta dada su ID, pero con sus preguntas asociadas
        survey = self.repo.get_by_id(survey_id)
        if not survey:
            return None 
        else:
            questions = []
            for qs in survey.question_surveys:    # qs es cada QuestionSurveys
                questions.append({
                "id_question_survey": qs.id,
                "question_text": qs.question.text,
                "psicometric_variable": qs.question.psicometric_variable
    })