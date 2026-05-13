"""
Schemas para la integración con el servicio de IA de Burnout.
Mantiene sincronización con schemas del AI-service.
"""

from pydantic import BaseModel, Field
from typing import List
from uuid import UUID


class WorkerBurnoutFeaturesResponse(BaseModel):
    """
    Respuesta de la vista vw_worker_burnout_features.
    Todos los campos necesarios para predicción de IA.
    """
    worker_id: UUID = Field(..., description="ID único del trabajador")
    
    # Datos laborales
    assigned_tasks: int = Field(..., ge=0, description="Tareas asignadas")
    completed_tasks: int = Field(..., ge=0, description="Tareas completadas")
    absences: int = Field(..., ge=0, description="Ausencias")
    employee_calls: int = Field(..., ge=0, description="Llamadas de empleado")
    completion_rate: float = Field(..., ge=0.0, le=1.0, description="Tasa completación (0-1)")
    seniority_years: float = Field(..., ge=0, description="Años de antigüedad")
    
    # Índices
    rank_index: int = Field(..., ge=1, description="Nivel de rango")
    group_index: int = Field(..., ge=1, description="Índice de grupo")
    
    # Datos personales
    age: int = Field(..., ge=18, le=70, description="Edad del trabajador")
    gender_enc: int = Field(..., ge=0, le=1, description="Género codificado (0=F, 1=M)")
    
    # Modalidad y sede
    worker_type_enc: int = Field(..., ge=0, le=1, description="Tipo trabajo (0=Hibrida, 1=Remoto)")
    location_enc: int = Field(..., ge=1, description="Índice de ubicación/sede")
    
    # Métricas psicométricas
    avg_agotamiento: float = Field(..., ge=1.0, le=5.0, description="Promedio agotamiento (1-5)")
    avg_despersonalizacion: float = Field(..., ge=1.0, le=5.0, description="Promedio despersonalizacion (1-5)")
    eficacia_invertida: float = Field(..., ge=1.0, le=5.0, description="Eficacia invertida (6-promedio)")


class BurnoutPredictionRequest(BaseModel):
    """
    Request para obtener predicción de burnout de un trabajador.
    """
    worker_id: UUID
    survey_id: UUID


class BurnoutPredictionResponse(BaseModel):
    """
    Response con predicción de burnout del AI service.
    """
    worker_id: UUID
    burnout_class: str = Field(..., description="Clasificación: Muy Bajo, Bajo, Medio, Moderado, Alto")
    burnout_confidence: float = Field(..., ge=0.0, le=1.0, description="Probabilidad de la clase predicha")
    probabilities: dict[str, float] = Field(..., description="Distribución de probabilidades por clase")
    reasons: List[str]
    suggestion: str = Field(..., description="Sugerencias de intervenciones que puede realizar la compañía con los empleados de acuerdo a su nivel de burnout")
