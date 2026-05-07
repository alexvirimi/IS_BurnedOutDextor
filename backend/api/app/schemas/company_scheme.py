from fastapi import Form
from pydantic import BaseModel
from uuid import UUID
from datetime import date 

class CompanyCreate (BaseModel):                # Crea los detalles empresariales de un empleado
    id_worker: UUID
    assigned_tasks: int
    completed_tasks: int
    absences: int  
    employee_calls: int  
    worker_type: str  
    location: str
    start_date: date
    @classmethod
    def as_form(cls, 
                id_worker: UUID = Form(...), 
                assigned_tasks: int = Form(...), 
                completed_tasks: int = Form(...), 
                absences: int = Form(...),  
                employee_calls: int = Form(...),  
                worker_type: str = Form(...),  
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