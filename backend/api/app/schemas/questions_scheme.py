from pydantic import BaseModel
from uuid import UUID

class QuestionCreate(BaseModel):                # para crear una pregunta se necesita el texto (la pregunta como tal) y asociarle la variable psicometrica que evalúa
    text: str
    psicometric_variable: str
    
class QuestionResponse(BaseModel):
    id: UUID
    text: str
    psicometric_variable: str
    model_config = {"from_attributes": True}    # Devuelve todos los parametros de una pregunta.
    
