import uuid
from typing import TYPE_CHECKING
from sqlalchemy import (
    String, 
    Integer, 
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .answer import Answer
    from .workers import Worker
    from .result import Result
    
class IdentityMapping(Base):
    __tablename__ = 'identity_mapping'
    
    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    
    id_worker: Mapped[uuid.UUID] = mapped_column(       
    String(36),
    ForeignKey('worker.id')   
    
    )  
    
    hash_user: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 hash for anonymity"
    
    worker: Mapped[Worker] = relationship(back_populates='mapping')
    results: Mapped[list[Result]] = relationship(back_populates='identity_mapping')
    answers: Mapped[list[Answer]] = relationship(back_populates='identity_mapping')