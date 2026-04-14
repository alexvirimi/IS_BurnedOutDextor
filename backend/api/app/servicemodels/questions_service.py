from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Question
from sqlalchemy.orm import Session 
from uuid import UUID

# Tendrá CRUD completo, sin embargo será solo C+R por ahora.
class QuestionService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(Question, db)                # modelo + sesión
        
    def get_questions(self):
        return self.repo.get_all()                  # obtiene todas las preguntas que existen
    
    def get_question(self, id: UUID):
        return self.repo.get_by_id(id)              # obtiene todos los detalles de una pregunta dada su UUID
    
    def create_question(self, data: dict):          # crea una pregunta dados todos sus parámetros
        return self.repo.create(data)
    
# TO DO:
# - Crear la función de Update
# - Crear la función de Delete