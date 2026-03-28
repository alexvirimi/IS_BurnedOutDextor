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
    from .groups import Group
    from .identity_mapping import IdentityMapping
    from .area import Area
    from .question_surveys import QuestionSurveys

class Answer(Base):
    __tablename__ = 'answer'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    hash_name: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey('rank.id')
    )
    id_group: Mapped[uuid.UUID] = mapped_column(
        String (36),
        ForeignKey('group.id')
    )
    id_area: Mapped[uuid.UUID] = mapped_column(
        String (36),
        ForeignKey('area.id')
    )
    id_questionsurveys: Mapped[uuid.UUID] = mapped_column(
        String (36),
        ForeignKey('question_surveys.id')
    )
    answer_value: Mapped[int] = mapped_column(Integer)
    answer_date:  Mapped[Date] = mapped_column(Date)
    
    group: Mapped[Group] = relationship(back_populates='answers')
    mappings: Mapped[IdentityMapping] = relationship(back_populates='answers')
    questionsurveys: Mapped[QuestionSurveys] = relationship (back_populates='answers') 
    area: Mapped[Area] = relationship (back_populates='answers')
    #results = Mapped[list[]]