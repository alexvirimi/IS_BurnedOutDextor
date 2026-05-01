from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from fastapi import Form

class QuestionCreate(BaseModel):                # para crear una pregunta se necesita el texto (la pregunta como tal) y asociarle la variable psicometrica que evalúa
    text: str
    psicometric_variable: str
    @classmethod
    def as_form(cls, 
                text: str = Form(...), 
                psicometric_variable: str = Form(...)):
        return cls(text=text, psicometric_variable=psicometric_variable)
    
class QuestionUpdate(BaseModel):                # para actualizar una pregunta, los campos son opcionales para permitir actualizaciones parciales
    text: Optional[str] = Field(None, description="Question text")
    psicometric_variable: Optional[str] = Field(None, description="Psicometric variable")
    
    @classmethod
    def as_form(cls, 
                text: Optional[str] = Form(None), 
                psicometric_variable: Optional[str] = Form(None)):
        # Solo incluir campos que son diferentes de None
        data = {}
        if text is not None:
            data['text'] = text
        if psicometric_variable is not None:
            data['psicometric_variable'] = psicometric_variable
        return cls(**data)
    
    # Cambiar los cuadros por field en lugar de form permite que sea posible enviar respuestas en unos sí y en otros no (dejarlos en blanco)
    # Esto es lo que realmente permite modificar solo un campo. Aprendí esto por las malas.
    
class QuestionResponse(BaseModel):
    id: UUID
    text: str
    psicometric_variable: str
    model_config = {"from_attributes": True}    # Devuelve todos los parametros de una pregunta.
    
