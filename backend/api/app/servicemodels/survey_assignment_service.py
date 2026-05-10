# Servicio para gestionar asignaciones de encuestas a trabajadores

from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import SurveyWorkerAssignment, Surveys, Worker, Answer, QuestionSurveys
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import and_, func


class SurveyAssignmentService:
    def __init__(self, db: Session):
        self.repo = ur(SurveyWorkerAssignment, db)
        self.db = db
    

    
    def assign_survey_to_workers(self, survey_id: UUID, worker_ids: list[UUID]):
        # Validar que la encuesta existe
        survey = ur(Surveys, self.db).get_by_id(survey_id)
        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe"
            )
        
        # Validar que todos los workers existen
        for worker_id in worker_ids:
            worker = ur(Worker, self.db).get_by_id(worker_id)
            if not worker:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El trabajador {worker_id} no existe"
                )
        
        # Crear asignaciones
        created_assignments = []
        for worker_id in worker_ids:
            # Verificar que no exista ya
            existing = self.db.query(SurveyWorkerAssignment).filter(
                and_(
                    SurveyWorkerAssignment.id_survey == survey_id,
                    SurveyWorkerAssignment.id_worker == worker_id
                )
            ).first()
            
            if not existing:
                assignment = SurveyWorkerAssignment(
                    id_survey=survey_id,
                    id_worker=worker_id
                )
                self.db.add(assignment)
                created_assignments.append(assignment)
        
        self.db.commit()
        for a in created_assignments:
            self.db.refresh(a)
        
        return created_assignments
    
    def assign_survey_to_workers_bulk(self, survey_ids: list[UUID], worker_ids: list[UUID]):

        created = []
        for survey_id in survey_ids:
            for worker_id in worker_ids:
                assignments = self.assign_survey_to_workers(survey_id, [worker_id])
                created.extend(assignments)
        
        return created
    
    
    def can_worker_respond_survey(self, worker_id: UUID, survey_id: UUID) -> bool:
        
        # Verificar que existe asignación
        assignment = self.db.query(SurveyWorkerAssignment).filter(
            and_(
                SurveyWorkerAssignment.id_survey == survey_id,
                SurveyWorkerAssignment.id_worker == worker_id
            )
        ).first()
        
        if not assignment:
            return False
        
        return True
    
    def get_missing_answers(self, worker_id: UUID, survey_id: UUID) -> list[UUID]:
        """
        Obtiene qué preguntas de una encuesta el worker AÚN NO ha respondido.
        Retorna lista de question_survey.id
        """
        # Obtener todas las preguntas de la encuesta
        all_questions = self.db.query(QuestionSurveys).filter(
            QuestionSurveys.id_survey == survey_id
        ).all()
        
        # Obtener preguntas ya respondidas por este worker
        answered_question_ids = self.db.query(Answer.id_question_survey.distinct()).filter(
            and_(
                Answer.id_worker == worker_id,
                QuestionSurveys.id_survey == survey_id
            )
        ).join(QuestionSurveys).all()
        
        answered_ids = {a[0] for a in answered_question_ids}
        
        # Preguntas faltantes
        missing = [q.id for q in all_questions if q.id not in answered_ids]
        
        return missing
    
    # ============================================
    # MIS ENCUESTAS (Para el worker)
    # ============================================
    
    def get_my_surveys(self, worker_id: UUID):
        """
        Obtiene las encuestas asignadas a este worker.
        Con info de si ya respondió o no.
        """
        assignments = self.db.query(SurveyWorkerAssignment).filter(
            SurveyWorkerAssignment.id_worker == worker_id
        ).all()
        
        my_surveys = []
        for assignment in assignments:
            survey = assignment.survey
            
            # Contar preguntas
            questions_count = self.db.query(func.count(QuestionSurveys.id)).filter(
                QuestionSurveys.id_survey == survey.id
            ).scalar()
            
            # ¿Ya respondí TODAS las preguntas?
            answered_count = self.db.query(func.count(Answer.id.distinct())).filter(
                and_(
                    Answer.id_worker == worker_id,
                    Answer.id_question_survey.in_(
                        self.db.query(QuestionSurveys.id).filter(
                            QuestionSurveys.id_survey == survey.id
                        )
                    )
                )
            ).scalar()
            
            already_responded = answered_count == questions_count and questions_count > 0
            
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
    
    # ============================================
    # GESTIÓN DE ASIGNACIONES
    # ============================================
    
    def remove_assignment(self, assignment_id: UUID):
        """Eliminar una asignación (RRHH)"""
        assignment = ur(SurveyWorkerAssignment, self.db).get_by_id(assignment_id)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignación no encontrada"
            )
        
        return ur(SurveyWorkerAssignment, self.db).delete_by_id(assignment_id)
    
    def get_survey_assignments(self, survey_id: UUID):
        """Obtener todos los workers asignados a una encuesta"""
        assignments = self.db.query(SurveyWorkerAssignment).filter(
            SurveyWorkerAssignment.id_survey == survey_id
        ).all()
        
        return [{
            "assignment_id": a.id,
            "worker_id": a.id_worker,
            "worker_name": a.worker.name,
            "created_at": a.created_at
        } for a in assignments]
    
    def get_worker_assignments(self, worker_id: UUID):
        """Obtener todas las encuestas asignadas a un worker"""
        assignments = self.db.query(SurveyWorkerAssignment).filter(
            SurveyWorkerAssignment.id_worker == worker_id
        ).all()
        
        return [{
            "assignment_id": a.id,
            "survey_id": a.id_survey,
            "survey_name": a.survey.name,
            "created_at": a.created_at
        } for a in assignments]
