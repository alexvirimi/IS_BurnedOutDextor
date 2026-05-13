# Esquemas para gestionar información empresarial de trabajadores.

from fastapi import Form
from pydantic import BaseModel, field_validator, model_validator
from uuid import UUID
from datetime import date 
from app.dbmodels.company import WorkerTypeEnum  # ✅ Importa el Enum


class CompanyCreate(BaseModel):
    # Información empresarial de un empleado
    id_worker: UUID
    assigned_tasks: int
    completed_tasks: int
    absences: int  
    employee_calls: int  
    worker_type: WorkerTypeEnum  # ✅ Usa el Enum, no str
    location: str
    start_date: date

    # ❌ ELIMINA este validator - el Enum ya valida automáticamente
    # @field_validator('worker_type')
    # @classmethod
    # def worker_type_valid_value(cls, v: str) -> str:
    #     ...

    @field_validator('completed_tasks', 'absences', 'employee_calls', 'assigned_tasks')
    @classmethod
    def non_negative(cls, v: int) -> int:
        """Validate non-negative integers"""
        if v < 0:
            raise ValueError("El valor no puede ser negativo")
        return v

    @model_validator(mode="after")
    def completed_le_assigned(self) -> "CompanyCreate":
        """Validate that completed_tasks does not exceed assigned_tasks"""
        if self.completed_tasks > self.assigned_tasks:
            raise ValueError(
                f"Las tareas completadas ({self.completed_tasks}) no pueden exceder las tareas asignadas ({self.assigned_tasks})"
            )
        return self

    @classmethod
    def as_form(cls, 
                id_worker: UUID = Form(...), 
                assigned_tasks: int = Form(...), 
                completed_tasks: int = Form(...), 
                absences: int = Form(...),  
                employee_calls: int = Form(...),  
                worker_type: WorkerTypeEnum = Form(...),  # ✅ Usa el Enum
                location: str = Form(...),
                start_date: date = Form(...)):
        return cls(
            id_worker=id_worker, 
            assigned_tasks=assigned_tasks, 
            completed_tasks=completed_tasks, 
            absences=absences,  
            employee_calls=employee_calls,  
            worker_type=worker_type,  
            location=location,
            start_date=start_date
        )


class CompanyResponse(BaseModel):
    # Respuesta con información empresarial completa
    id: UUID
    id_worker: UUID
    assigned_tasks: int
    completed_tasks: int
    absences: int
    employee_calls: int
    worker_type: WorkerTypeEnum  
    location: str
    start_date: date
    model_config = {"from_attributes": True}