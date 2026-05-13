# Servicio para gestionar operaciones de encuestas.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Surveys
from app.dbmodels.surveys import SurveyStatus
from sqlalchemy.orm import Session
from uuid import UUID
from app.dbmodels import Question, QuestionSurveys
from sqlalchemy.orm import joinedload
from typing import Optional
from datetime import date as date_type


class SurveyService:
    def __init__(self, db: Session) -> None:
        self.repo = ur(Surveys, db)
        self.db = db

    def calculate_survey_status(self, aperture_date: date_type, finishing_date: date_type) -> str:
        """
        Calculate survey status automatically based on current date and survey dates.
        - If today < aperture_date: status = "cerrada" (not open yet)
        - If aperture_date <= today <= finishing_date: status = "activa" (open)
        - If today > finishing_date: status = "cerrada" (closed)
        """
        today = date_type.today()
        
        if today < aperture_date:
            return SurveyStatus.CERRADA.value
        elif aperture_date <= today <= finishing_date:
            return SurveyStatus.ABIERTA.value
        else:  # today > finishing_date
            return SurveyStatus.CERRADA.value

    def get_surveys(self):
        return self.repo.get_all()

    def get_survey(self, id: UUID):
        return self.repo.get_by_id(id)

    def create_survey(self, data: dict):
        """
        Create a new survey with automatic status calculation.
        The status field provided in data is ignored; it's calculated automatically.
        """
        aperture_date = data.get('aperture_date')
        finishing_date = data.get('finishing_date')
        
        # Calculate automatic status
        calculated_status = self.calculate_survey_status(aperture_date, finishing_date)
        data['status'] = calculated_status
        
        return self.repo.create(data)

    def update_survey(self, id: UUID, data: dict) -> Optional[Surveys]:
        """
        Actualiza parcialmente una encuesta.
        Si se actualizan las fechas, recalcula el estado automáticamente.
        Solo modifica los campos presentes en `data`; los demás permanecen intactos.
        Retorna la encuesta actualizada, o None si no existe.
        """
        survey = self.db.query(Surveys).filter(Surveys.id == id).first()
        if not survey:
            return None
        
        # If dates are being updated, recalculate status
        if 'aperture_date' in data or 'finishing_date' in data:
            aperture_date = data.get('aperture_date', survey.aperture_date)
            finishing_date = data.get('finishing_date', survey.finishing_date)
            calculated_status = self.calculate_survey_status(aperture_date, finishing_date)
            data['status'] = calculated_status
        elif 'status' in data:
            # If user explicitly sets status, validate it's a valid enum value
            if data['status'] not in [SurveyStatus.ABIERTA.value, SurveyStatus.CERRADA.value]:
                from app.exceptions import BusinessValidationError

                raise BusinessValidationError(f"Invalid status. Must be 'activa' or 'cerrada'")
        
        for field, value in data.items():
            setattr(survey, field, value)
        self.db.commit()
        self.db.refresh(survey)
        return survey

    def get_survey_complete(self, survey_id: UUID, db: Session):
        """
        Obtiene una encuesta completa con todas sus preguntas y opciones de respuesta.
        El estado se calcula automáticamente.
        """
        survey = db.query(Surveys).options(
            joinedload(Surveys.question_surveys).joinedload(QuestionSurveys.question)
        ).filter(Surveys.id == survey_id).first()

        if not survey:
            return None

        # Recalculate status based on current date
        calculated_status = self.calculate_survey_status(survey.aperture_date, survey.finishing_date)

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
            "status": calculated_status,
            "questions": questions,
            "answer_options": answer_options,
        }