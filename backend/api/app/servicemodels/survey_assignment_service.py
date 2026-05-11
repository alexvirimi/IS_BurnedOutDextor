from app.controllers.cr_controller import UniversalRepository as ur

from app.dbmodels import (
    SurveyWorkerAssignment,
    Surveys,
    Worker,
    Answer,
    QuestionSurveys
)

from sqlalchemy.orm import Session

from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy import and_, func


class SurveyAssignmentService:

    def __init__(self, db: Session):

        self.repo = ur(SurveyWorkerAssignment, db)

        self.survey_repo = ur(Surveys, db)

        self.worker_repo = ur(Worker, db)

        self.db = db

    def assign_survey_to_workers(
        self,
        survey_id: UUID,
        worker_ids: list[UUID]
    ):

        survey = self.survey_repo.get_by_id(survey_id)

        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe"
            )

        created_assignments = []

        for worker_id in worker_ids:

            worker = self.worker_repo.get_by_id(worker_id)

            if not worker:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El trabajador {worker_id} no existe"
                )

            existing = self.db.query(
                SurveyWorkerAssignment
            ).filter(
                and_(
                    SurveyWorkerAssignment.id_survey == survey_id,
                    SurveyWorkerAssignment.id_worker == worker_id
                )
            ).first()

            if existing:
                continue

            assignment = self.repo.create({
                "id_survey": survey_id,
                "id_worker": worker_id
            })

            created_assignments.append(assignment)

        return created_assignments

    def assign_survey_to_workers_bulk(
        self,
        survey_ids: list[UUID],
        worker_ids: list[UUID]
    ):

        created = []

        for survey_id in survey_ids:

            assignments = self.assign_survey_to_workers(
                survey_id,
                worker_ids
            )

            created.extend(assignments)

        return created

    def can_worker_respond_survey(
        self,
        worker_id: UUID,
        survey_id: UUID
    ) -> bool:

        assignment = self.db.query(
            SurveyWorkerAssignment
        ).filter(
            and_(
                SurveyWorkerAssignment.id_survey == survey_id,
                SurveyWorkerAssignment.id_worker == worker_id
            )
        ).first()

        return assignment is not None

    def get_missing_answers(
        self,
        worker_id: UUID,
        survey_id: UUID
    ) -> list[UUID]:

        all_questions = self.db.query(
            QuestionSurveys
        ).filter(
            QuestionSurveys.id_survey == survey_id
        ).all()

        answered_question_ids = self.db.query(
            Answer.id_question_survey.distinct()
        ).join(
            QuestionSurveys
        ).filter(
            and_(
                Answer.id_worker == worker_id,
                QuestionSurveys.id_survey == survey_id
            )
        ).all()

        answered_ids = {a[0] for a in answered_question_ids}

        return [
            q.id
            for q in all_questions
            if q.id not in answered_ids
        ]

    def get_my_surveys(self, worker_id: UUID):

        assignments = self.db.query(
            SurveyWorkerAssignment
        ).filter(
            SurveyWorkerAssignment.id_worker == worker_id
        ).all()

        my_surveys = []

        for assignment in assignments:

            survey = assignment.survey

            questions_count = self.db.query(
                func.count(QuestionSurveys.id)
            ).filter(
                QuestionSurveys.id_survey == survey.id
            ).scalar()

            answered_count = self.db.query(
                func.count(Answer.id.distinct())
            ).filter(
                and_(
                    Answer.id_worker == worker_id,
                    Answer.id_question_survey.in_(
                        self.db.query(
                            QuestionSurveys.id
                        ).filter(
                            QuestionSurveys.id_survey == survey.id
                        )
                    )
                )
            ).scalar()

            already_responded = (
                answered_count == questions_count
                and questions_count > 0
            )

            my_surveys.append({
                "id": survey.id,
                "name": survey.name,
                "aperture_date": str(survey.aperture_date),
                "finishing_date": str(survey.finishing_date),
                "status": survey.status,
                "assignment_id": assignment.id,
                "questions_count": questions_count,
                "already_responded": already_responded
            })

        return my_surveys

    def remove_assignment(self, assignment_id: UUID):

        assignment = self.repo.get_by_id(assignment_id)

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignación no encontrada"
            )

        self.repo.delete_by_id(assignment_id)

        return True

    def get_survey_assignments(self, survey_id: UUID):

        assignments = self.db.query(
            SurveyWorkerAssignment
        ).filter(
            SurveyWorkerAssignment.id_survey == survey_id
        ).all()

        return [
            {
                "assignment_id": a.id,
                "worker_id": a.id_worker,
                "worker_name": a.worker.name,
                "created_at": a.created_at
            }
            for a in assignments
        ]

    def get_worker_assignments(self, worker_id: UUID):

        assignments = self.db.query(
            SurveyWorkerAssignment
        ).filter(
            SurveyWorkerAssignment.id_worker == worker_id
        ).all()

        return [
            {
                "assignment_id": a.id,
                "survey_id": a.id_survey,
                "survey_name": a.survey.name,
                "created_at": a.created_at
            }
            for a in assignments
        ]