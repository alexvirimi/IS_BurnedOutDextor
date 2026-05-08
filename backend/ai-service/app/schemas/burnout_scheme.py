from pydantic import BaseModel, Field, model_validator
from uuid import UUID


class WorkerInput(BaseModel):
    # Identificador (worker.id)
    worker_id: UUID

    # Datos laborales (tabla: company)
    # Field (...) indica que el campo es obligatorio, ge=0 para validar que no sea negativo
    assigned_tasks: int = Field(..., ge=0)
    completed_tasks: int = Field(..., ge=0)
    absences: int = Field(..., ge=0)
    employee_calls: int = Field(..., ge=0)
    completion_rate: float = Field(..., ge=0)  # completed/assigned (calculado)
    # (today - start_date).days / 365 (calculado)
    seniority_years: float = Field(..., ge=0)

    # Rango y grupo (tablas: rank, group)
    rank_index:  UUID
    group_index: UUID

    # Datos personales (tabla: workers)
    age: int = Field(..., ge=18, le=100)  # rango de edad laboral
    gender_enc: int = Field(..., ge=0)  # worker.gender codificado

    # Modalidad y sede (tabla:company)
    work_mode_enc: int = Field(..., ge=0)  # company.work_type codificado
    location_enc: int = Field(..., ge=0)  # company.location codificado

    # Encuesta MBI-GS (tabla: question + answer)
    # promedio de respuestas a preguntas de agotamiento (calculado)
    avg_agotamiento: float = Field(..., ge=1.0, le=5.0)
    # promedio de respuestas a preguntas de despersonalización (calculado)
    avg_despersonalizacion: float = Field(..., ge=1.0, le=5.0)
    # 6 - promedio de respuestas a preguntas de eficacia
    eficacia_invertida: float = Field(..., ge=1.0, le=5.0)

    @model_validator(mode="after")
    def validate_tasks(self):
        if self.completed_tasks > self.assigned_tasks:
            raise ValueError("completed_tasks no puede superar assigned_tasks")
        return self


class BurnoutPredictionResult(BaseModel):
    worker_id:           str
    burnout_score:       float  # probabilidad de burnout (0.0 - 1.0)
    burnout_class:       str   # "Muy Bajo" | "Bajo" | "Medio" | "Moderado" | "Alto"
    burnout_confidence:  float  # probabilidad de burnout (0.0 - 1.0)
    probabilities:       dict  # {"Muy Bajo": 0.03, "Bajo": 0.08, ...}
