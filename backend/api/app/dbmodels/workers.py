

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
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
    from .ranks import Rank
    from .company import Company
    from .answer import Answer
    from .result import Result

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
    gender: Mapped[str] = mapped_column(String(20))  # Demographics for survey analysis

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