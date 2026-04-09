

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
    
    burnout_score: Mapped[str] = mapped_column(String(36))
    
    id_worker: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('worker.id')
    )
    
    id_group: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey ('group.id')
    )
    
    id_area: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey ('area.id')
    )
    
    id_survey: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey ('survey.id')
    )
    
    generation_date: Mapped[Date] = mapped_column(Date)

    workers: Mapped[Worker] = relationship(back_populates='results')
    survey: Mapped[Surveys] = relationship(back_populates='results')
    area: Mapped[Area] = relationship(back_populates='results')
    group: Mapped[Group] = relationship(back_populates='results')
