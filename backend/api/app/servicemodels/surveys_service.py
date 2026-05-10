# Servicio para gestionar operaciones de encuestas.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Surveys
from sqlalchemy.orm import Session
from uuid import UUID
from app.dbmodels import Question, QuestionSurveys
from sqlalchemy.orm import joinedload
from typing import Optional

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
    
    def get_survey_complete(self, survey_id: UUID, db: Session):
        """
        Obtiene una encuesta completa con todas sus preguntas y opciones de respuesta.
        Retorna estructura lista para que el frontend responda.
        """
        from sqlalchemy.orm import joinedload
        
        survey = db.query(Surveys).options(
            joinedload(Surveys.question_surveys).joinedload(QuestionSurveys.question)
        ).filter(Surveys.id == survey_id).first()
        
        if not survey:
            return None
        
        # Construir las preguntas con su ID de relación (question_survey.id)
        questions = []
        for qs in survey.question_surveys:
            questions.append({
                "id": qs.id,  # Este es el question_survey.id necesario para responder
                "question_text": qs.question.text,
                "psicometric_variable": qs.question.psicometric_variable
            })
        
        # Opciones de respuesta estándar (escala 1-5)
        answer_options = [
            {"value": 1, "label": "Nunca"},
            {"value": 2, "label": "Casi nunca"},
            {"value": 3, "label": "A veces"},
            {"value": 4, "label": "Casi siempre"},
            {"value": 5, "label": "Siempre"}
        ]
        
        return {
            "id": survey.id,
            "name": survey.name,
            "aperture_date": survey.aperture_date,
            "finishing_date": survey.finishing_date,
            "status": survey.status,
            "questions": questions,
            "answer_options": answer_options
        }
    