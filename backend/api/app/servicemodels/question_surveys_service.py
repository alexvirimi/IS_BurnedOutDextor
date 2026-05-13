# Servicio para gestionar relaciones pregunta-encuesta.

from app.controllers.crud_controller import UniversalRepository as ur
from app.dbmodels import QuestionSurveys, Question
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.question_surveys_scheme import QuestionSurveyBulkCreate
from uuid import UUID as UUIDType

# Business-required psicometric variables
REQUIRED_PSICO_IDS = {
    UUIDType("7bfe6646-c400-4913-93ec-bcff12c67987"): "Despersonalizacion",
    UUIDType("9b76e819-3e37-4d52-ad7d-00bbecdab3d0"): "Eficacia",
    UUIDType("c8dfdbb2-6761-4bb7-ab29-7b2c615e11a5"): "Agotamiento",
}


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
        # Crear relación pregunta-encuesta con validación de negocio
        db = self.repo.db
        from app.exceptions import BusinessValidationError

        required_ids = list(REQUIRED_PSICO_IDS.keys())

        survey_id = data.get('id_survey')
        question_id = data.get('id_question')

        # Variables presentes actualmente en la encuesta (solo requeridas)
        existing_rows = (
            db.query(Question.psicometric_variable_id)
            .join(QuestionSurveys, Question.id == QuestionSurveys.id_question)
            .filter(
                QuestionSurveys.id_survey == survey_id,
                Question.psicometric_variable_id.in_(required_ids),
            )
            .distinct()
            .all()
        )
        existing_found = {r[0] for r in existing_rows}

        # Variable aportada por la pregunta entrante (si es requerida)
        incoming_row = (
            db.query(Question.psicometric_variable_id)
            .filter(
                Question.id == question_id,
                Question.psicometric_variable_id.in_(required_ids),
            )
            .distinct()
            .first()
        )
        incoming_found = {incoming_row[0]} if incoming_row else set()

        combined = existing_found.union(incoming_found)
        missing_ids = [pid for pid in required_ids if pid not in combined]
        if missing_ids:
            missing = [REQUIRED_PSICO_IDS[pid] for pid in missing_ids]
            raise BusinessValidationError(
                f"Asignación inválida: faltan preguntas para las variables: {missing}"
            )

        # Passed validation — create relation
        obj = QuestionSurveys(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update_question_survey(self, id: UUID, data: dict):
        # Actualizar relación existente con validación de negocio
        db = self.repo.db
        from app.exceptions import BusinessValidationError

        obj = db.query(QuestionSurveys).get(id)
        if not obj:
            return None

        # Determine target survey and question after update
        target_survey = data.get('id_survey', obj.id_survey)
        target_question = data.get('id_question', obj.id_question)

        required_ids = list(REQUIRED_PSICO_IDS.keys())

        # Question IDs that will belong to the target survey after update
        qid_rows = (
            db.query(QuestionSurveys.id_question)
            .filter(QuestionSurveys.id_survey == target_survey)
            .filter(QuestionSurveys.id != id)
            .all()
        )
        qids = {r[0] for r in qid_rows}
        qids.add(target_question)

        # Fetch psicometric variables for those question ids (only required)
        var_rows = (
            db.query(Question.psicometric_variable_id)
            .filter(Question.id.in_(list(qids)))
            .filter(Question.psicometric_variable_id.in_(required_ids))
            .distinct()
            .all()
        )
        found = {r[0] for r in var_rows}
        missing_ids = [pid for pid in required_ids if pid not in found]
        if missing_ids:
            missing = [REQUIRED_PSICO_IDS[pid] for pid in missing_ids]
            raise BusinessValidationError(f"Actualización inválida: faltan preguntas para las variables: {missing}")

        # Apply update
        for key, value in data.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete_question_survey(self, id: UUID):
        # Eliminar relación pregunta-encuesta con validación de negocio
        db = self.repo.db
        from app.exceptions import BusinessValidationError

        obj = db.query(QuestionSurveys).get(id)
        if not obj:
            return False

        required_ids = list(REQUIRED_PSICO_IDS.keys())

        # Remaining question IDs after deletion
        qid_rows = (
            db.query(QuestionSurveys.id_question)
            .filter(QuestionSurveys.id_survey == obj.id_survey)
            .filter(QuestionSurveys.id != id)
            .all()
        )
        qids = {r[0] for r in qid_rows}

        # Fetch psicometric variables for remaining questions
        var_rows = (
            db.query(Question.psicometric_variable_id)
            .filter(Question.id.in_(list(qids)))
            .filter(Question.psicometric_variable_id.in_(required_ids))
            .distinct()
            .all()
        )
        found = {r[0] for r in var_rows}
        missing_ids = [pid for pid in required_ids if pid not in found]
        if missing_ids:
            missing = [REQUIRED_PSICO_IDS[pid] for pid in missing_ids]
            raise BusinessValidationError(f"Eliminación inválida: quedarán faltantes para las variables: {missing}")

        db.delete(obj)
        db.commit()
        return True


    def assign_questions(self, payload):
        """
        Asignar múltiples preguntas a una encuesta en lote.

        Validación: después de la asignación, la encuesta debe contener al menos
        una pregunta asociada a cada psicométrico requerido. La validación se
        realiza con consultas optimizadas que retornan los psicométricos
        presentes (DISTINCT) sin cargar entidades completas.
        """
        db = self.repo.db
        required_ids = list(REQUIRED_PSICO_IDS.keys())

        # Variables ya presentes en la encuesta (solo las requeridas)
        existing_rows = (
            db.query(Question.psicometric_variable_id)
            .join(QuestionSurveys, Question.id == QuestionSurveys.id_question)
            .filter(
                QuestionSurveys.id_survey == payload.id_survey,
                Question.psicometric_variable_id.in_(required_ids),
            )
            .distinct()
            .all()
        )
        existing_found = {r[0] for r in existing_rows}

        # Variables aportadas por las preguntas entrantes (solo las requeridas)
        incoming_rows = (
            db.query(Question.psicometric_variable_id)
            .filter(
                Question.id.in_(payload.question_ids),
                Question.psicometric_variable_id.in_(required_ids),
            )
            .distinct()
            .all()
        )
        incoming_found = {r[0] for r in incoming_rows}

        combined = existing_found.union(incoming_found)

        missing_ids = [pid for pid in required_ids if pid not in combined]
        if missing_ids:
            missing = [REQUIRED_PSICO_IDS[pid] for pid in missing_ids]
            from app.exceptions import BusinessValidationError

            raise BusinessValidationError(
                f"Asignación inválida: faltan preguntas para las variables: {missing}"
            )

        # Passed validation — create relations
        relations = []
        for question_id in payload.question_ids:
            relation = QuestionSurveys(
                id_survey=payload.id_survey,
                id_question=question_id,
            )
            db.add(relation)
            relations.append(relation)

        db.commit()
        for r in relations:
            db.refresh(r)
        return relations