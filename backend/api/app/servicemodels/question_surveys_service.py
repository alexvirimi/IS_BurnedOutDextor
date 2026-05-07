# Servicio para gestionar relaciones pregunta-encuesta.

from app.controllers.crud_controller import UniversalRepository as ur
from app.dbmodels import QuestionSurveys
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.question_surveys_scheme import QuestionSurveyBulkCreate

class QuestionSurveyService:
    # CRUD para relaciones entre preguntas y encuestas
    def __init__(self, db: Session) -> None:
        self.repo = ur(QuestionSurveys, db)
    
    def get_question_surveys(self):
        # Obtener todas las relaciones pregunta-encuesta
        return self.repo.get_all()
    
    def get_question_survey(self, id: UUID):
        # Obtener relación específica por ID
        return self.repo.get_by_id(id)
    
    def create_question_survey(self, data: dict):
        # Crear relación pregunta-encuesta
        return self.repo.create(data)
    
    def update_question_survey(self, id: UUID, data: dict):
        # Actualizar relación existente
        return self.repo.update(id, data)
    
    def delete_question_survey(self, id: UUID):
        # Eliminar relación pregunta-encuesta
        return self.repo.delete_by_id(id)
    
  
    def assign_questions(self, payload):
        # Asignar múltiples preguntas a una encuesta en lote
        relations = []
        for question_id in payload.question_ids:
            relation = QuestionSurveys(
                id_survey=payload.id_survey,
                id_question=question_id
            )
            self.repo.db.add(relation)
            relations.append(relation)

        self.repo.db.commit()
        for r in relations:
            self.repo.db.refresh(r)
        return relations
