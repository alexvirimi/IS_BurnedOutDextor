import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    String, 
    ForeignKey,
    Date,
    Integer
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .question_surveys import QuestionSurveys
    from .answer import Answer

class Surveys(Base):
    __tablename__ = 'surveys'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )

    name:Mapped[str]= mapped_column (String(200))
    aperture_date: Mapped[Date]=mapped_column(Date)
    finishing_date: Mapped[Date]=mapped_column(Date)
    status: Mapped[str]= mapped_column (String(200))
    
    question_surveys: Mapped[list[QuestionSurveys]]= relationship(back_populates='survey')
    answers: Mapped[Optional[list[Answer]]] = relationship (back_populates= 'survey')