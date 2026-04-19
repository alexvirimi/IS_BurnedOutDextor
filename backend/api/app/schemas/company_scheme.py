from pydantic import BaseModel
from uuid import UUID
from datetime import date 

class CompanyCreate (BaseModel):                # Crea los detalles empresariales de un empleado
    assigned_tasks: int
    completed_tasks: int
    absences: int  
    employee_calls: int  
    worker_type: str  
    location: str
    start_date: date

class CompanyResponse(BaseModel):
    id: UUID
    id_worker: UUID
    assigned_tasks: int
    completed_tasks: int
    absences: int  
    employee_calls: int  
    worker_type: str  
    location: str
    start_date: date
    model_config = {"from_attributes": True}    # devuelve toda la información (id y nombre) de un rango