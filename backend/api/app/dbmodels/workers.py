from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
import enum
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    UUID,
    Boolean,
    Enum,
    CheckConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .groups import Group
    from .ranks import Rank
    from .company import Company
    from .answer import Answer
    from .result import Result
    from .survey_assignments import SurveyWorkerAssignment


class GenderEnum(str, enum.Enum):
    """Worker gender enum - restricted to M and F"""
    MALE = "M"
    FEMALE = "F"


class Worker(Base):
    __tablename__ = 'worker'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100))
    last_names: Mapped[str] = mapped_column(String(150))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(
        Enum(GenderEnum, native_enum=False),
        nullable=False
    )

    id_group: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey('group.id')
    )
    id_rank: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('rank.id')
    )

    group: Mapped[Group] = relationship(back_populates='workers', foreign_keys=[id_group])
    group_leader: Mapped[Group] = relationship(back_populates='worker_leader', foreign_keys='Group.id_leader')
    rank: Mapped[Rank] = relationship(back_populates='workers')
    answers: Mapped[list[Answer]] = relationship(back_populates='workers')
    company: Mapped[Company] = relationship(back_populates='worker')
    results: Mapped[list[Result]]= relationship (back_populates='workers')
    survey_assignments: Mapped[list[SurveyWorkerAssignment]] = relationship(back_populates='worker', cascade='all, delete-orphan')
