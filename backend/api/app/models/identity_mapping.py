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
    __tablename__='identity_mapping'
    
    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    id_worker: Mapped[uuid.UUID] = mapped_column(
        String (36),
        ForeignKey ('workers.id')
    )
    
    hname: Mapped[str] = mapped_column(String(100))
    
    worker: Mapped[Worker] = relationship ('mapping')
    results: Mapped[list[Result]] = relationship ('mappings')
    answer: Mapped[list[Answer]] = relationship ('mappings')