# Servicio para gestionar operaciones de respuestas de encuestas.

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Answer
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.dbmodels import Group, Worker, Area, QuestionSurveys
from datetime import date

class AnswerService:
    def __init__(self, db: Session):
        self.repo = ur(Answer, db)
        self.db = db         

    def get_answers(self):
        return self.repo.get_all()       

    def get_answer_by_id(self, id: UUID):
        return self.repo.get_by_id(id)

    def create_answer(self, data: dict):
        group = ur(Group, self.db).get_by_id(data["id_group"])
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El grupo no existe"
            )
        worker = ur(Worker, self.db).get_by_id(data["id_worker"])
        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe"
            )
        area = ur(Area, self.db).get_by_id(data["id_area"])
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área no existe"
            )
        question_survey = ur(QuestionSurveys, self.db).get_by_id(data["id_question_survey"])
        if not question_survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta no existe"
            )    
        return self.repo.create(data)
    
    def create_bulk_answers(
        self,
        worker_id: UUID,
        survey_id: UUID,
        answers_data: list[dict]
    ):
        """
        Crea múltiples respuestas de una encuesta de una vez.
        """

        from app.dbmodels import Surveys

        # Validar worker
        worker = ur(Worker, self.db).get_by_id(worker_id)

        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe"
            )

        # Validar encuesta
        survey = ur(Surveys, self.db).get_by_id(survey_id)

        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe"
            )

        # Evitar responder encuesta dos veces
        existing_answers = self.db.query(Answer).join(
            QuestionSurveys
        ).filter(
            Answer.id_worker == worker_id,
            QuestionSurveys.id_survey == survey_id
        ).first()

        if existing_answers:
            raise HTTPException(
                status_code=400,
                detail="Ya respondiste esta encuesta"
            )

        # Obtener group y area
        group = ur(Group, self.db).get_by_id(worker.id_group)

        if not group:
            raise HTTPException(
                status_code=404,
                detail="El grupo del trabajador no existe"
            )

        area = ur(Area, self.db).get_by_id(group.id_area)

        if not area:
            raise HTTPException(
                status_code=404,
                detail="El área del grupo no existe"
            )

        created_answers = []

        for answer_data in answers_data:

            # Validar que la pregunta pertenece a la encuesta
            question_survey = self.db.query(
                QuestionSurveys
            ).filter(
                QuestionSurveys.id == answer_data["id_question_survey"],
                QuestionSurveys.id_survey == survey_id
            ).first()

            if not question_survey:
                raise HTTPException(
                    status_code=404,
                    detail=f"La pregunta {answer_data['id_question_survey']} no pertenece a esta encuesta"
                )

            answer_create_data = {
                "id_worker": worker_id,
                "id_group": worker.id_group,
                "id_area": group.id_area,
                "id_question_survey": answer_data["id_question_survey"],
                "value": answer_data["value"],
                "created_at": date.today()
            }

            created_answer = self.repo.create(answer_create_data)

            created_answers.append(created_answer)

        return created_answers
    
    def create_answer_from_user(
        self,
        worker_id: UUID,
        question_survey_id: UUID,
        value: int
    ):
        """
        Crea una respuesta desde el usuario autenticado.
        """

        worker = ur(Worker, self.db).get_by_id(worker_id)

        if not worker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe"
            )

        group = ur(Group, self.db).get_by_id(worker.id_group)

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El grupo del trabajador no existe"
            )

        area = ur(Area, self.db).get_by_id(group.id_area)

        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área del grupo no existe"
            )

        question_survey = ur(
            QuestionSurveys,
            self.db
        ).get_by_id(question_survey_id)

        if not question_survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta en la encuesta no existe"
            )

        # Evitar respuestas duplicadas
        existing_answer = self.db.query(Answer).filter(
            Answer.id_worker == worker_id,
            Answer.id_question_survey == question_survey_id
        ).first()

        if existing_answer:
            raise HTTPException(
                status_code=400,
                detail="Ya respondiste esta pregunta"
            )

        answer_data = {
            "id_worker": worker_id,
            "id_group": worker.id_group,
            "id_area": group.id_area,
            "id_question_survey": question_survey_id,
            "value": value,
            "created_at": date.today()
        }

        return self.repo.create(answer_data)
    
    def get_answers_by_worker(self, worker_id: UUID):
        """Obtiene todas las respuestas de un usuario"""
        return self.db.query(Answer).filter(Answer.id_worker == worker_id).all()
    
    def get_answers_by_survey(self, survey_id: UUID):
        """Obtiene todas las respuestas de una encuesta"""
        return self.db.query(Answer).join(
            QuestionSurveys
        ).filter(QuestionSurveys.id_survey == survey_id).all()
    
    def create_answers_bulk(self, answers: list):
        # Crear múltiples respuestas en lote
        results = []
        for answer in answers:
            created = self.create_answer(answer.model_dump())
            results.append(created)
        return results
    