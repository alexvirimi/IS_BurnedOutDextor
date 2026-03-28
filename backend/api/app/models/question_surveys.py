<<<<<<< HEAD
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    String, 
    ForeignKey,
    Date,
    Integer,
    UUID
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
    from .answer import Answer

class QuestionSurveys(Base):
    
    __tablename__ = 'question_survey'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )

    id_survey: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('survey.id')
    )
    id_question: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('question.id')
    )      
    
    question: Mapped[Question] = relationship(back_populates='question_surveys')
    survey: Mapped[Surveys] = relationship(back_populates='question_surveys')
    answers: Mapped[list[Answer]] = relationship(back_populates='question_survey')
=======
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
>>>>>>> a691221 (actualization of main branch)
