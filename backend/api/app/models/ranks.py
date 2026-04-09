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
    from .workers import Worker

    
class Rank(Base):
    
    __tablename__ = 'rank'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    rank_name: Mapped[str] = mapped_column (String(100))

    workers: Mapped[list[Worker]]=relationship(back_populates='rank')