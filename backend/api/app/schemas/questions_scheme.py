from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class QuestionCreate(BaseModel):                # para crear una pregunta se necesita el texto (la pregunta como tal) y asociarle la variable psicometrica que evalúa
    text: str
    psicometric_variable: str
    
class QuestionUpdate(BaseModel):                # para actualizar una pregunta, los campos son opcionales para permitir actualizaciones parciales
    text: Optional[str] = None                  # El optional es para que se puedan mandar unos si y otros no
    psicometric_variable: Optional[str] = None
    
class QuestionResponse(BaseModel):
    id: UUID
    text: str
    psicometric_variable: str
    model_config = {"from_attributes": True}    # Devuelve todos los parametros de una pregunta.
    
