from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List
from fastapi import Form
from app.schemas.psicometric_variable_scheme import PsicometricVariableResponse

class QuestionCreate(BaseModel):
    # para crear una pregunta se necesita el texto (la pregunta como tal) y asociarle la variable psicometrica que evalúa
    text: str
    psicometric_variable_id: UUID

    @classmethod
    def as_form(cls, text: str = Form(...), psicometric_variable_id: UUID = Form(...)):
        return cls(text=text, psicometric_variable_id=psicometric_variable_id)

class QuestionUpdate(BaseModel):
    # para actualizar una pregunta, los campos son opcionales para permitir actualizaciones parciales
    text: Optional[str] = Field(None, description="Question text")
    psicometric_variable_id: Optional[UUID] = Field(None, description="Psicometric variable ID")

    @classmethod
    def as_form(cls, text: Optional[str] = Form(None), psicometric_variable_id: Optional[UUID] = Form(None)):
        # Solo incluir campos que son diferentes de None
        data = {}
        if text is not None:
            data["text"] = text
        if psicometric_variable_id is not None:
            data["psicometric_variable_id"] = psicometric_variable_id
        return cls(**data)
    # Cambiar los cuadros por field en lugar de form permite que sea posible enviar respuestas en unos sí y en otros no (dejarlos en blanco)
    # Esto es lo que realmente permite modificar solo un campo. Aprendí esto por las malas.

class QuestionResponse(BaseModel):
    id: UUID
    text: str
    psicometric_variable: PsicometricVariableResponse

    model_config = {"from_attributes": True}
    # Devuelve todos los parametros de una pregunta.