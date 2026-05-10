from pydantic import BaseModel, Field, model_validator
from uuid import UUID


class WorkerInput(BaseModel):
    # Identificador único para trazabilidad entre servicios (worker.id)
    worker_id: UUID

    # Datos laborales
    assigned_tasks: int = Field(..., ge=0)
    completed_tasks: int = Field(..., ge=0)
    absences: int = Field(..., ge=0)
    employee_calls: int = Field(..., ge=0)
    # completed/assigned (calculado)
    completion_rate: float = Field(..., ge=0.0, le=1.0)
    # (today - start_date).days / 365 (calculado)
    seniority_years: float = Field(..., ge=0)

    # Datos personales (tabla: workers)
    age: int = Field(..., ge=18, le=70)  # rango de edad laboral
    gender_enc: int = Field(..., ge=0)  # worker.gender codificado

    # Modalidad y sede (tabla:company)
    worker_type_enc: int = Field(..., ge=0)  # company.work_type codificado
    location_enc: int = Field(..., ge=0)  # company.location codificado

    # Encuesta MBI-GS (tabla: question + answer)
    # promedio de respuestas a preguntas de agotamiento (calculado)
    avg_agotamiento: float = Field(..., ge=1.0, le=5.0)
    # promedio de respuestas a preguntas de despersonalización (calculado)
    avg_despersonalizacion: float = Field(..., ge=1.0, le=5.0)
    # 6 - promedio de respuestas a preguntas de eficacia (calculado)
    eficacia_invertida: float = Field(..., ge=1.0, le=5.0)

    @model_validator(mode="after")
    def validate_tasks(self):
        if self.completed_tasks > self.assigned_tasks:
            raise ValueError("completed_tasks no puede superar assigned_tasks")
        return self


class BurnoutPredictionResult(BaseModel):
    worker_id: UUID
    burnout_class: str  # "Muy Bajo" | "Bajo" | "Medio" | "Moderado" | "Alto"
    # Probabilidad de la clase predicha (0.0 - 1.0)
    burnout_score: float = Field(..., ge=0.0, le=1.0)
    # Mapa completo: {"Alto": 0.85, "Medio": 0.10, ...}
    probabilities: dict[str, float]
