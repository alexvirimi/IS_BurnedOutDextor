from app.controllers.crud_controller import UniversalRepository as ur
from app.dbmodels import Question, QuestionSurveys, Surveys, PsicometricVariable
from sqlalchemy.orm import Session
from uuid import UUID

class QuestionService:
    # CRUD completo para preguntas de encuestas
    def __init__(self, db: Session) -> None:
        self.repo = ur(Question, db)
        self.db = db
        
    def _validate_psicometric_variable(self, psicometric_variable_id: UUID):
        psicometric_variable = self.db.query(PsicometricVariable).filter(PsicometricVariable.id == psicometric_variable_id).first()
        if not psicometric_variable:
            from app.exceptions import BusinessValidationError

            raise BusinessValidationError(f"PsicometricVariable con ID {psicometric_variable_id} no encontrada.")
        return psicometric_variable

    def get_questions(self):
        # Obtener todas las preguntas
        return self.repo.get_all()
    
    def get_question(self, id: UUID):
        # Obtener pregunta por ID
        return self.repo.get_by_id(id)
    
    def create_question(self, data: dict):
        # Crear nueva pregunta
        psicometric_variable_id = data.get("psicometric_variable_id")
        if psicometric_variable_id:
            self._validate_psicometric_variable(psicometric_variable_id)
        return self.repo.create(data)
    
    def update_question(self, id: UUID, data: dict):
        # Actualizar pregunta existente
        psicometric_variable_id = data.get("psicometric_variable_id")
        if psicometric_variable_id:
            self._validate_psicometric_variable(psicometric_variable_id)
        return self.repo.update(id, data)
    
    def delete_question(self, id: UUID):
        # Eliminar pregunta
        return self.repo.delete_by_id(id)
    
    def get_surveys_by_question(self, id: UUID):
        # Obtener encuestas asociadas a una pregunta
        surveys = self.db.query(Surveys).join(
            QuestionSurveys,
            Surveys.id == QuestionSurveys.id_survey
        ).filter(
            QuestionSurveys.id_question == id
        ).all()
        return surveys