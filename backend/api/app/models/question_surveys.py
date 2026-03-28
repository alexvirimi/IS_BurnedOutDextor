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
    from .surveys import Surveys
    from .questions import Question

class QuestionSurveys(Base):
    
    __tablename__ = 'question_survey'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )

    id_survey: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey('surveys.id')
    )
    id_question: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey('question.id')
    )      
    
    question: Mapped[Question] = relationship(back_populates='question_surveys')
    survey: Mapped[Surveys] = relationship(back_populates='question_surveys')