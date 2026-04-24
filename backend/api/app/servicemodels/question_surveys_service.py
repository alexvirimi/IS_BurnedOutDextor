from app.controllers.crud_controller import UniversalRepository as ur
from app.dbmodels import QuestionSurveys
from sqlalchemy.orm import Session 
from uuid import UUID

# Deberá tener CRUD completo, sin embargo será solo C+R por ahora.
class QuestionSurveyService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(QuestionSurveys, db)         # modelo + sesión
    
    def get_question_surveys(self):
        return self.repo.get_all()                  # obtiene todas las relaciones preguntas+encuesta que existen
    
    def get_question_survey(self, id: UUID):
        return self.repo.get_by_id(id)              # obtiene todos los detalles de una relación pregunta+encuesta dada su UUID
    
    def create_question_survey(self, data: dict):          # crea una relación pregunta+encuesta dados todos sus parámetros
        return self.repo.create(data)
    
    def update_question_survey(self, id: UUID, data: dict):  # actualiza una relación pregunta+encuesta dada su UUID y los datos a actualizar
        return self.repo.update(id, data)
    
    def delete_question_survey(self, id: UUID):             # elimina una relación pregunta+encuesta dada su UUID
        return self.repo.delete_by_id(id)
    
# TO DO:
# - Crear la función de Update
# - Crear la función de Delete