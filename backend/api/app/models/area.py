import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    String, 
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .groups import Group
    from .answer import Answer
    from .result import Result



class Area(Base):
    __tablename__ = 'area'
    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    name: Mapped[str] = mapped_column(String(100))

    groups: Mapped[list[Group]] = relationship(back_populates='area')
    answers:Mapped[list[Answer]] = relationship(back_populates='area')
    results:Mapped[list[Result]] = relationship(back_populates='area')

