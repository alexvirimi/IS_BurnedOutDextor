# Servicio para gestionar operaciones de respuestas de encuestas.

import asyncio
import logging
import threading
from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Answer
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from uuid import UUID
from fastapi import HTTPException, status
from app.dbmodels import Group, Worker, Area, QuestionSurveys, Surveys
from datetime import date
from app.database import SessionLocal
from app.dbmodels import Result

logger = logging.getLogger(__name__)

# ─── Constante canónica ───────────────────────────────────────────────────────
# Una sola fuente de verdad para el valor de estado. Si el backend cambia el
# string (ej. "FINALIZADA") solo hay que actualizar aquí.
_STATUS_FINALIZADA = "finalizada"


def _assert_survey_is_open(survey: Surveys) -> None:
    """
    Lanza HTTP 422 si la encuesta ya fue finalizada.
    Reutiliza el patrón de HTTPException existente en el proyecto.
    Normaliza a minúsculas para evitar fallos por mayúsculas inconsistentes.
    """
    if survey.status.strip().lower() == _STATUS_FINALIZADA:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"La encuesta '{survey.name}' ya fue finalizada "
                "y no acepta nuevas respuestas."
            ),
        )


def _check_survey_completion(db: Session, worker_id: UUID, survey_id: UUID) -> bool:
    """
    Verifica si un trabajador ha respondido TODAS las preguntas de una encuesta.
    Retorna True si la encuesta está completa para ese trabajador.
    """
    try:
        # Contar total de preguntas en la encuesta
        total_questions = db.query(func.count(QuestionSurveys.id)).filter(
            QuestionSurveys.id_survey == survey_id
        ).scalar()

        # Contar respuestas del trabajador para esta encuesta
        answered_questions = db.query(func.count(Answer.id)).join(
            QuestionSurveys
        ).filter(
            Answer.id_worker == worker_id,
            QuestionSurveys.id_survey == survey_id
        ).scalar()

        logger.info(
            f"Survey completion check - Worker: {worker_id}, "
            f"Survey: {survey_id}, Total: {total_questions}, "
            f"Answered: {answered_questions}"
        )

        return answered_questions >= total_questions
    except Exception as e:
        logger.error(f"Error checking survey completion: {str(e)}")
        return False


async def _trigger_burnout_prediction(
    worker_id: UUID, survey_id: UUID
) -> bool:
    """
    Llama asincronamente al endpoint de predicción de burnout.
    Captura errores sin bloquear el flujo principal.
    Retorna True si la predicción fue exitosa, False en caso contrario.
    """
    # Crear una nueva sesión independiente para la tarea en background.
    db = SessionLocal()
    try:
        # Importar aquí para evitar circular imports
        from app.servicemodels.burnout_service import BurnoutService

        logger.info(
            f"Triggering burnout prediction for worker {worker_id}, "
            f"survey {survey_id} (background task)"
        )

        # IDempotency: comprobar a nivel de aplicación si ya existe un resultado
        existing = (
            db.query(Result)
            .filter(Result.id_worker == worker_id, Result.id_survey == survey_id)
            .order_by(Result.generation_date.desc())
            .first()
        )

        if existing:
            logger.info(
                f"Skipping prediction: existing Result found for worker {worker_id}, "
                f"survey {survey_id} (id={existing.id})"
            )
            return False

        # Llamar al servicio de predicción (es async)
        result = await BurnoutService.predict_worker_burnout(
            db, worker_id, survey_id
        )

        logger.info(
            f"Burnout prediction completed successfully for worker {worker_id}: "
            f"Class={result.burnout_class}, Confidence={result.burnout_confidence}"
        )

        return True

    except HTTPException as he:
        logger.warning(
            f"HTTP Error in burnout prediction for worker {worker_id}: "
            f"{he.status_code} - {he.detail}"
        )
        return False

    except Exception as e:
        logger.error(
            f"Unexpected error in burnout prediction for worker {worker_id}: "
            f"{str(e)}"
        )
        return False

    finally:
        db.close()


class AnswerService:
    def __init__(self, db: Session):
        self.repo = ur(Answer, db)
        self.db = db

    def get_answers(self):
        return self.repo.get_all()

    def get_answer_by_id(self, id: UUID):
        return self.repo.get_by_id(id)

    def create_answer(self, data: dict):
        """Ruta RRHH — valida todos los FK y el estado de la encuesta."""
        group = ur(Group, self.db).get_by_id(data["id_group"])
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El grupo no existe",
            )

        worker = ur(Worker, self.db).get_by_id(data["id_worker"])
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe",
            )

        area = ur(Area, self.db).get_by_id(data["id_area"])
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área no existe",
            )

        question_survey = ur(QuestionSurveys, self.db).get_by_id(
            data["id_question_survey"]
        )
        if not question_survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta no existe",
            )

        # ── Validación: encuesta no finalizada ───────────────────────────────
        survey = ur(Surveys, self.db).get_by_id(question_survey.id_survey)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta asociada no existe",
            )
        _assert_survey_is_open(survey)

        return self.repo.create(data)

    def create_bulk_answers(
        self, worker_id: UUID, survey_id: UUID, answers_data: list[dict]
    ):
        """
        Crea múltiples respuestas de una encuesta de una vez.
        Valida el estado antes de procesar cualquier respuesta.
        
        NUEVA FUNCIONALIDAD:
        - Después de crear las respuestas, verifica si la encuesta está completa
        - Si está completa, dispara automáticamente la predicción de burnout
        - La predicción se ejecuta de forma no bloqueante (fire-and-forget)
        """
        worker = ur(Worker, self.db).get_by_id(worker_id)
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe",
            )

        survey = ur(Surveys, self.db).get_by_id(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe",
            )

        # ── Validación: encuesta no finalizada ───────────────────────────────
        # Se verifica UNA SOLA VEZ antes del loop, no en cada iteración.
        _assert_survey_is_open(survey)

        created_answers = []
        for answer_data in answers_data:
            question_survey = ur(QuestionSurveys, self.db).get_by_id(
                answer_data["id_question_survey"]
            )
            if not question_survey:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"La pregunta {answer_data['id_question_survey']} "
                        "no existe en la encuesta"
                    ),
                )

            answer_create_data = {
                "id_worker": worker_id,
                "id_group": worker.id_group,
                "id_area": (
                    worker.group.id_area if worker.group else None
                ),
                "id_question_survey": answer_data["id_question_survey"],
                "value": answer_data["value"],
                "created_at": date.today(),
            }
            created_answers.append(self.repo.create(answer_create_data))

        # ─────────────────────────────────────────────────────────────────────
        # NUEVA LÓGICA: Verificar completitud y disparar predicción de burnout
        # ─────────────────────────────────────────────────────────────────────
        if _check_survey_completion(self.db, worker_id, survey_id):
            logger.info(
                f"Survey {survey_id} completed by worker {worker_id}. "
                f"Triggering burnout prediction..."
            )
            
            # Dispara la predicción en background sin bloquear la respuesta
            try:
                # Ejecutar la tarea de predicción en un hilo separado que crea
                # su propio event loop usando asyncio.run. Esto evita el error
                # "There is no current event loop in thread 'AnyIO worker thread'".
                threading.Thread(
                    target=lambda: asyncio.run(_trigger_burnout_prediction(worker_id, survey_id)),
                    daemon=True,
                ).start()
                logger.info(
                    f"Burnout prediction thread started for worker {worker_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to start prediction thread: {str(e)}. "
                    f"Continuing without blocking..."
                )
                # No relanzar - permitir que la respuesta se retorne de todos modos

        return created_answers

    def create_answer_from_user(
        self, worker_id: UUID, question_survey_id: UUID, value: int
    ):
        """
        Crea una respuesta desde el usuario autenticado.
        Valida el estado de la encuesta antes de persistir.
        
        NUEVA FUNCIONALIDAD:
        - Después de crear la respuesta, verifica si la encuesta está completa
        - Si está completa, dispara automáticamente la predicción de burnout
        - La predicción se ejecuta de forma no bloqueante (fire-and-forget)
        """
        worker = ur(Worker, self.db).get_by_id(worker_id)
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe",
            )

        group = ur(Group, self.db).get_by_id(worker.id_group)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El grupo del trabajador no existe",
            )

        area = ur(Area, self.db).get_by_id(group.id_area)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área del grupo no existe",
            )

        question_survey = ur(QuestionSurveys, self.db).get_by_id(question_survey_id)
        if not question_survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta en la encuesta no existe",
            )

        # ── Validación: encuesta no finalizada ───────────────────────────────
        survey = ur(Surveys, self.db).get_by_id(question_survey.id_survey)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta asociada no existe",
            )
        _assert_survey_is_open(survey)

        answer_data = {
            "id_worker": worker_id,
            "id_group": worker.id_group,
            "id_area": group.id_area,
            "id_question_survey": question_survey_id,
            "value": value,
            "created_at": date.today(),
        }
        created_answer = self.repo.create(answer_data)

        # ─────────────────────────────────────────────────────────────────────
        # NUEVA LÓGICA: Verificar completitud y disparar predicción de burnout
        # ─────────────────────────────────────────────────────────────────────
        survey_id = question_survey.id_survey
        
        if _check_survey_completion(self.db, worker_id, survey_id):
            logger.info(
                f"Survey {survey_id} completed by worker {worker_id}. "
                f"Triggering burnout prediction..."
            )
            
            # Dispara la predicción en background sin bloquear la respuesta
            try:
                threading.Thread(
                    target=lambda: asyncio.run(_trigger_burnout_prediction(worker_id, survey_id)),
                    daemon=True,
                ).start()
                logger.info(
                    f"Burnout prediction thread started for worker {worker_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to start prediction thread: {str(e)}. "
                    f"Continuing without blocking..."
                )
                # No relanzar - permitir que la respuesta se retorne de todos modos

        return created_answer

    def get_answers_by_worker(self, worker_id: UUID):
        return self.db.query(Answer).filter(Answer.id_worker == worker_id).all()

    def get_answers_by_survey(self, survey_id: UUID):
        return (
            self.db.query(Answer)
            .join(QuestionSurveys)
            .filter(QuestionSurveys.id_survey == survey_id)
            .all()
        )

    def create_answers_bulk(self, answers: list):
        results = []
        for answer in answers:
            created = self.create_answer(answer.model_dump())
            results.append(created)
        return results