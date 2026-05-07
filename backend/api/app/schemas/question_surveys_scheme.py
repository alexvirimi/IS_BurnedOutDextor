from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from fastapi import Form
class QuestionSurveyCreate(BaseModel):
    id_survey: UUID
    id_question: UUID
    @classmethod
    def as_form(cls, id_survey: UUID = Form(...), id_question: UUID = Form(...)):
        return cls(id_survey=id_survey, id_question=id_question)

class QuestionSurveyUpdate(BaseModel):                # para actualizar una pregunta, los campos son opcionales para permitir actualizaciones parciales
    id_survey: Optional[UUID] = Field(None, description="ID de la encuesta")                 # El optional es para que se puedan mandar unos si y otros no
    id_question: Optional[UUID] = Field(None, description="ID de la pregunta")              # El optional es para que se puedan mandar unos si y otros no
    @classmethod
    def as_form(cls, id_survey: Optional[UUID] = Form(None), id_question: Optional[UUID] = Form(None)):
        # Solo incluir campos que son diferentes de None
        data = {}
        if id_survey is not None:
            data['id_survey'] = id_survey
        if id_question is not None:
            data['id_question'] = id_question
        return cls(**data)

class QuestionSurveyResponse(BaseModel):
    id: UUID
    id_survey: UUID
    id_question: UUID
    model_config = {"from_attributes": True}    # Devuelve todos los parametros de una relación entre preguntas y encuestas.
    
class QuestionSurveyBulkCreate(BaseModel):
    id_survey: UUID
    questions: List[str]  
    
class AssignQuestions(BaseModel):
    id_survey: UUID
    question_ids: list[UUID]
    @classmethod
    def as_form(cls, id_survey: UUID, question_ids: list[UUID]):
        return cls(id_survey=id_survey, question_ids=question_ids)
    
    # Nota para Mario: Sí se podía poner form, en el swagger lo que te va a aparecer es una lista
    # Puedes irle añadiendo más cuadritos para añadir más cosas, creo que así es mejor, sino
    # Solo tienes que quitar el = Form(...)
    
    # MENTIRA, NO SÉ POR QUÉ PERO SE ROMPE Y NO SÉ COMO ARREGLARLO
    # ASÍ SE QUEDA
    
    # luego con más calma, ahora mismo no tengo mente para esto
    # Si funciona, no se toca