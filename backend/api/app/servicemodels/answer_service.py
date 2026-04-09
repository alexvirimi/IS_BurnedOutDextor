from app.controllers.cr_controller import UniversalRepository as ur
from app.dbmodels import Answer
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from app.dbmodels import Group, Worker, Area, QuestionSurvey

#En la tabla area solo se pueden realizar las lecturas de la misma.
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
        question_survey = ur(QuestionSurvey, self.db).get_by_id(data["id_question_survey"])
        if not question_survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La pregunta no existe"
            )    
        return self.repo.create(data)    
