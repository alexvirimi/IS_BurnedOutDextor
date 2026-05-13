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

        # =========================================================
        # UPDATE EXISTING RESULT
        # =========================================================

        if existing:

            existing.burnout_confidence = data["burnout_confidence"]

            existing.id_group = data["id_group"]

            existing.id_area = data["id_area"]

            existing.flag = data.get(
                "flag",
                existing.flag
            )

            existing.burnout_class = data.get(
                "burnout_class",
                existing.burnout_class
            )

            existing.burnout_reasons = data.get(
                "burnout_reasons",
                existing.burnout_reasons
            )

            existing.suggested_intervention = data.get(
                "suggested_intervention",
                existing.suggested_intervention
            )

            existing.intervention_status = data.get(
                "intervention_status",
                existing.intervention_status
            )

            existing.hr_comment = data.get(
                "hr_comment",
                existing.hr_comment
            )

            existing.generation_date = data.get(
                "generation_date",
                existing.generation_date
            )

            self.db.commit()

            self.db.refresh(existing)

            return existing

        # =========================================================
        # CREATE NEW RESULT
        # =========================================================

        result_data = {
            "id": data.get("id"),
            "burnout_confidence": data["burnout_confidence"],
            "id_worker": data["id_worker"],
            "id_group": data["id_group"],
            "id_area": data["id_area"],
            "id_survey": data["id_survey"],
            "generation_date": data["generation_date"],
            "flag": data.get("flag", False),
            "burnout_class": data.get("burnout_class"),
            "burnout_reasons": data.get("burnout_reasons"),
            "suggested_intervention": data.get("suggested_intervention"),
            "intervention_status": data.get(
                "intervention_status",
                "Pendiente"
            ),
            "hr_comment": data.get("hr_comment")
        }

        return self.repo.create(result_data)

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