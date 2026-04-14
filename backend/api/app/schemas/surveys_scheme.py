from pydantic import BaseModel
from uuid import UUID
from sqlalchemy import Date

class SurveyCreate(BaseModel):
    name: str
    apreture_date: Date
    finishing_date: Date
    status: str

class SurveyResponse():
    id: UUID
    name: str
    apreture_date: Date
    finishing_date: Date
    status: str
    model_config = {"from_attributes": True}