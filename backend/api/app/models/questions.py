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
    from .groups import Group
    from .identity_mapping import IdentityMapping
    from .area import Area
    from .question_surveys import QuestionSurveys

class Question(Base):
    __tablename__ = 'question'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    
    text: Mapped[str] = mapped_column(String(500))  # Survey question text\n    
    psicometric_variable: Mapped[str] = mapped_column(String(100))  # Associated psychological variable"
    
    question_surveys: Mapped[list[QuestionSurveys]]= relationship(back_populates='question')