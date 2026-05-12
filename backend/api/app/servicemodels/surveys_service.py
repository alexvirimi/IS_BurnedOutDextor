# Servicio para gestionar operaciones de encuestas.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Surveys
from sqlalchemy.orm import Session
from uuid import UUID
from app.dbmodels import Question, QuestionSurveys
from sqlalchemy.orm import joinedload
from typing import Optional


class SurveyService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(Surveys, db)
        self.db = db

    def get_surveys(self):
        return self.repo.get_all()

    def get_survey(self, id: UUID):
        return self.repo.get_by_id(id)

    def create_survey(self, data: dict):
        return self.repo.create(data)

    def update_survey(self, id: UUID, data: dict) -> Optional[Surveys]:
        """
        Actualiza parcialmente una encuesta.
        Solo modifica los campos presentes en `data`; los demás permanecen intactos.
        Retorna la encuesta actualizada, o None si no existe.
        """
        survey = self.db.query(Surveys).filter(Surveys.id == id).first()
        if not survey:
            return None
        for field, value in data.items():
            setattr(survey, field, value)
        self.db.commit()
        self.db.refresh(survey)
        return survey

    def get_survey_complete(self, survey_id: UUID, db: Session):
        """
        Obtiene una encuesta completa con todas sus preguntas y opciones de respuesta.
        """
        survey = db.query(Surveys).options(
            joinedload(Surveys.question_surveys).joinedload(QuestionSurveys.question)
        ).filter(Surveys.id == survey_id).first()

        if not survey:
            return None

        questions = []
        for qs in survey.question_surveys:
            questions.append({
                "id": qs.id,
                "question_text": qs.question.text,
                "psicometric_variable": qs.question.psicometric_variable.name,
            })

        answer_options = [
            {"value": 1, "label": "Nunca"},
            {"value": 2, "label": "Casi nunca"},
            {"value": 3, "label": "A veces"},
            {"value": 4, "label": "Casi siempre"},
            {"value": 5, "label": "Siempre"},
        ]

        return {
            "id": survey.id,
            "name": survey.name,
            "aperture_date": survey.aperture_date,
            "finishing_date": survey.finishing_date,
            "status": survey.status,
            "questions": questions,
            "answer_options": answer_options,
        }
