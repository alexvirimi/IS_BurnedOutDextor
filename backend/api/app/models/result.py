import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    String, 
    ForeignKey,
    Date,
    Integer
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
    from .identity_mapping import IdentityMapping
    from .surveys import Surveys
    
class Result(Base):
    __tablename__ = 'results'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    
    burnout_score: Mapped[str] = mapped_column(String(36))
    
    hash_user: Mapped[str] = mapped_column (
        String,
        ForeignKey('identity_mapping.hash_user')
    )
    
    id_group: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey ('group.id')
    )
    
    id_area: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey ('area.id')
    )
    
    id_surveys: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey ('surveys.id')
    )
    
    generation_date: Mapped[Date] = mapped_column(Date)
    
    mappings: Mapped[IdentityMapping] = relationship(back_populates='results')
    #answer: Mapped[Answer] = relationship (back_populates='results')
    survey: Mapped[Surveys] = relationship (back_populates='results')
    area: Mapped[Area] = relationship (back_populates='results')
    group: Mapped[Group] = relationship (back_populates='results')