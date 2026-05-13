from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date


class InterventionReviewRequest(BaseModel):
    intervention_status: str = Field(
        ..., description="Pendiente | Aprobada | Rechazada | Ejecutada"
    )
    hr_comment: Optional[str] = Field(
        None, max_length=2000, description="Comentario de RRHH"
    )


class InterventionResponse(BaseModel):
    id:                     UUID
    burnout_class:          str
    burnout_confidence:     float
    suggested_intervention: Optional[str]
    intervention_status:    str
    hr_comment:             Optional[str]
    generation_date:        date

    model_config = {"from_attributes": True}
