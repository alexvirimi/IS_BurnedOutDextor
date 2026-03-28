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
    hash_user: Mapped[str] = mapped_column(
        String,
        ForeignKey('identity_mapping.hash_user')  # Anonymized reference to worker
    )
    id_group: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey('group.id')
    )
    id_area: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey('area.id')
    )
    id_question_survey: Mapped[uuid.UUID] = mapped_column(
        String(36),
        ForeignKey('question_survey.id')
    )
    value: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[Date] = mapped_column(Date)
    
    group: Mapped[Group] = relationship(back_populates='answers')
    identity_mapping: Mapped[IdentityMapping] = relationship(back_populates='answers')
    question_survey: Mapped[QuestionSurveys] = relationship(back_populates='answers')
    area: Mapped[Area] = relationship(back_populates='answers')
