from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKey,
    UUID,
    DateTime
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
    from .surveys import Surveys
    from .workers import Worker


class SurveyWorkerAssignment(Base):
    __tablename__ = 'survey_worker_assignment'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )

    id_survey: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('survey.id', ondelete='CASCADE')
    )

    id_worker: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('worker.id', ondelete='CASCADE')
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    survey: Mapped[Surveys] = relationship(back_populates='worker_assignments')
    worker: Mapped[Worker] = relationship(back_populates='survey_assignments')
