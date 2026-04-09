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
    from .question_surveys import QuestionSurveys
    from .result import Result

class Surveys(Base):
    __tablename__ = 'survey'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(String(200))
    aperture_date: Mapped[Date] = mapped_column(Date)
    finishing_date: Mapped[Date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(200))

    question_surveys: Mapped[list[QuestionSurveys]] = relationship(back_populates='survey')
    results: Mapped[list[Result]] = relationship(back_populates='survey')
