from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    String, 
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
    from .workers import Worker
    from .area import Area
    from .answer import Answer
    from .result import Result


class Group(Base):
    __tablename__ = 'group'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100))
    
    id_area: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('area.id')
    )
    id_leader: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('worker.id')
    )

    workers: Mapped[Optional[list[Worker]]] = relationship(back_populates='group', foreign_keys='Worker.id_group')
    worker_leader: Mapped[Worker] = relationship(back_populates='group_leader', foreign_keys='Group.id_leader')
    area: Mapped[Area] = relationship(back_populates='groups')
    answers:Mapped[list[Answer]] = relationship(back_populates='group')
    results: Mapped[list[Result]] = relationship(back_populates='group')
