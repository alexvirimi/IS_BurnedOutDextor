from __future__ import annotations

import uuid

from typing import TYPE_CHECKING

from datetime import date

from sqlalchemy import (
    ForeignKey,
    Date,
    UUID,
    Boolean,
    Numeric
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .area import Area
    from .groups import Group
    from .workers import Worker
    from .surveys import Surveys


class Result(Base):

    __tablename__ = 'result'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )

    burnout_score: Mapped[float] = mapped_column(
        Numeric(10, 4)
    )

    flag: Mapped[bool] = mapped_column(
        Boolean,
        default=False
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

    id_survey: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('survey.id')
    )

    generation_date: Mapped[date] = mapped_column(
        Date,
        default=date.today
    )

    workers: Mapped["Worker"] = relationship(
        back_populates='results'
    )

    survey: Mapped["Surveys"] = relationship(
        back_populates='results'
    )

    area: Mapped["Area"] = relationship(
        back_populates='results'
    )

    group: Mapped["Group"] = relationship(
        back_populates='results'
    )