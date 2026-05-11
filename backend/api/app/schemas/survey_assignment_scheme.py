# Esquemas para asignación de encuestas a trabajadores

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from fastapi import Form


class AssignSurveyToWorkers(BaseModel):
    """Asignar una encuesta a múltiples trabajadores específicos"""
    id_survey: UUID = Field(..., description="UUID de la encuesta")
    worker_ids: List[UUID] = Field(..., description="UUIDs de los trabajadores a los que asignar")
    
    @classmethod
    def as_form(cls, 
                id_survey: UUID = Form(...),
                worker_ids: str = Form(...)):  # JSON string
        import json
        return cls(id_survey=id_survey, worker_ids=json.loads(worker_ids))


class SurveyWorkerAssignmentResponse(BaseModel):
    id: UUID
    id_survey: UUID
    id_worker: UUID
    created_at: datetime
    model_config = {"from_attributes": True}


class MySurveyResponse(BaseModel):
    id: UUID
    name: str
    aperture_date: str
    finishing_date: str
    status: str
    assignment_id: UUID  # Para saber cuál es MI asignación
    questions_count: int = 0
    already_responded: bool = False
    
    model_config = {"from_attributes": True}


class BulkAssignSurveyToWorkers(BaseModel):
    """Asignar múltiples encuestas a múltiples trabajadores"""
    survey_ids: List[UUID] = Field(..., description="UUIDs de encuestas")
    worker_ids: List[UUID] = Field(..., description="UUIDs de trabajadores")
    
    @classmethod
    def as_form(cls,
                survey_ids: str = Form(...),
                worker_ids: str = Form(...)):
        import json
        return cls(survey_ids=json.loads(survey_ids), worker_ids=json.loads(worker_ids))
