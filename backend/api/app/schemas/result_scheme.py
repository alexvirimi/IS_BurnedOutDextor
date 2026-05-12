from pydantic import BaseModel, Field

from uuid import UUID

from datetime import date

from fastapi import Form

from typing import Optional


class UpdateFlagRequest(BaseModel):

    flag: bool


class ResultCreate(BaseModel):

    id_worker: UUID

    id_group: UUID

    id_area: UUID

    id_survey: UUID

    burnout_score: float

    generation_date: date = Field(
        default_factory=date.today
    )

    flag: Optional[bool] = False

    @classmethod
    def as_form(
        cls,
        id_worker: UUID = Form(...),
        id_group: UUID = Form(...),
        id_area: UUID = Form(...),
        id_survey: UUID = Form(...),
        burnout_score: float = Form(...),
        generation_date: date | None = Form(None),
        flag: bool = Form(False)
    ):

        return cls(
            id_worker=id_worker,
            id_group=id_group,
            id_area=id_area,
            id_survey=id_survey,
            burnout_score=burnout_score,
            generation_date=generation_date or date.today(),
            flag=flag
        )


class ResultResponse(BaseModel):

    id: UUID

    id_worker: UUID

    id_group: UUID

    id_area: UUID

    id_survey: UUID

    burnout_score: float

    generation_date: date

    flag: bool = False

    model_config = {
        "from_attributes": True
    }