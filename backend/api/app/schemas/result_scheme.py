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
    burnout_confidence: float
    burnout_class: str
    burnout_reasons: Optional[str] = None
    suggested_intervention: Optional[str] = None
    intervention_status: str = "Pendiente"
    hr_comment: Optional[str] = None
    generation_date: date = Field(default_factory=date.today)
    flag: Optional[bool] = False

    @classmethod
    def as_form(
        cls,
        id_worker: UUID = Form(...),
        id_group: UUID = Form(...),
        id_area: UUID = Form(...),
        id_survey: UUID = Form(...),
        burnout_confidence: float = Form(...),
        burnout_class: str = Form(...),
        burnout_reasons: Optional[str] = Form(None),
        suggested_intervention: Optional[str] = Form(None),
        intervention_status: str = Form("Pendiente"),
        hr_comment: Optional[str] = Form(None),
        generation_date: Optional[date] = Form(None),
        flag: bool = Form(False),
    ):
        return cls(
            id_worker=id_worker,
            id_group=id_group,
            id_area=id_area,
            id_survey=id_survey,
            burnout_confidence=burnout_confidence,
            burnout_class=burnout_class,
            burnout_reasons=burnout_reasons,
            suggested_intervention=suggested_intervention,
            intervention_status=intervention_status,
            hr_comment=hr_comment,
            generation_date=generation_date or date.today(),
            flag=flag,
        )


class ResultResponse(BaseModel):
    id: UUID
    id_worker: UUID
    id_group: UUID
    id_area: UUID
    id_survey: UUID
    burnout_confidence: float
    burnout_class: str
    burnout_reasons: Optional[str] = None
    suggested_intervention: Optional[str] = None
    intervention_status: str
    hr_comment: Optional[str] = None
    generation_date: date
    flag: bool = False

    model_config = {"from_attributes": True}