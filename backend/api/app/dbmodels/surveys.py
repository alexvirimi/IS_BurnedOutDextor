from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    String, 
    ForeignKey,
    Date,
    Integer,
    UUID,
    CheckConstraint,
    Enum,
    func,
    case
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    column_property
)
import enum
from datetime import date as date_type
from .survey_assignments import SurveyWorkerAssignment
from .base import Base

if TYPE_CHECKING:
    from .question_surveys import QuestionSurveys
    from .result import Result


class SurveyStatus(str, enum.Enum):
    """Survey status enum - represents survey availability"""
    ABIERTA = "activa"
    CERRADA = "cerrada"


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
    status: Mapped[str] = mapped_column(
        Enum(SurveyStatus, native_enum=False),
        default=SurveyStatus.CERRADA,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            'finishing_date > aperture_date',
            name='ck_survey_date_order'
        ),
    )

    question_surveys: Mapped[list[QuestionSurveys]] = relationship(back_populates='survey')
    results: Mapped[list[Result]] = relationship(back_populates='survey')
    worker_assignments: Mapped[list[SurveyWorkerAssignment]] = relationship(
        back_populates='survey'
    )