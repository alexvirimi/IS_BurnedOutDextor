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
    from .groups import Group
    from .area import Area
    from .question_surveys import QuestionSurveys
    from .workers import Worker
class Answer(Base):
    __tablename__ = 'answer'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    id_worker: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('worker.id')  
    )
    id_group: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('group.id')
    )
    id_area: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('area.id')
    )
    id_question_survey: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('question_survey.id')
    )
    value: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[Date] = mapped_column(Date)
    
    group: Mapped[Group] = relationship(back_populates='answers')
    workers: Mapped[list[Worker]] = relationship(back_populates='answers')
    question_survey: Mapped[QuestionSurveys] = relationship(back_populates='answers')
    area: Mapped[Area] = relationship(back_populates='answers')
