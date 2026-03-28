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

class Question(Base):
    __tablename__ = 'question'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    
    hash_name: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey('identity_mapping.hname')
    )    
    psicometric_var: Mapped[str]= mapped_column(String)
    
    question_surveys: Mapped[list[QuestionSurveys]]= relationship(back_populates='question')