from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from app.controllers.cr_controller import UniversalRepository as ur

from app.dbmodels import (
    Result,
    Group,
    Worker,
    Area,
    Surveys
)


class ResultService:

    def __init__(self, db: Session):

        self.repo = ur(Result, db)

        self.db = db

    def get_results(self):

        return self.repo.get_all()

    def get_result_by_id(self, id: UUID):

        return self.repo.get_by_id(id)

    def get_results_by_worker(self, worker_id: UUID):

        return self.db.query(Result).filter(
            Result.id_worker == worker_id
        ).all()

    def get_results_by_group(self, group_id: UUID):

        return self.db.query(Result).filter(
            Result.id_group == group_id
        ).all()

    def create_result(self, data: dict):

        group = ur(Group, self.db).get_by_id(
            data["id_group"]
        )

        if not group:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El grupo no existe"
            )

        worker = ur(Worker, self.db).get_by_id(
            data["id_worker"]
        )

        if not worker:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El trabajador no existe"
            )

        area = ur(Area, self.db).get_by_id(
            data["id_area"]
        )

        if not area:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El área no existe"
            )

        survey = ur(Surveys, self.db).get_by_id(
            data["id_survey"]
        )

        if not survey:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La encuesta no existe"
            )

        existing = self.db.query(Result).filter(
            Result.id_worker == data["id_worker"],
            Result.id_survey == data["id_survey"]
        ).first()

        if existing:

            existing.burnout_score = data["burnout_score"]

            existing.id_group = data["id_group"]

            existing.id_area = data["id_area"]

            existing.flag = data.get("flag", existing.flag)

            self.db.commit()

            self.db.refresh(existing)

            return existing

        return self.repo.create(data)

    def update_result_flag(
        self,
        result_id: UUID,
        flag: bool
    ):

        result = self.get_result_by_id(result_id)

        if not result:

            return None

        result.flag = flag

        self.db.commit()

        self.db.refresh(result)

        return result