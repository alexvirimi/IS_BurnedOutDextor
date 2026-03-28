import uuid
from typing import TYPE_CHECKING
from sqlalchemy import (
    String, 
    Integer,
    Date,
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .workers import Worker


class Company(Base):
    __tablename__ = 'company'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    id_worker: Mapped[uuid.UUID] = mapped_column(        
        String(36),
        ForeignKey('worker.id'),
        unique=True
    )  # One company record per worker    
    
    assigned_tasks: Mapped[int] = mapped_column(Integer, default=0)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0)
    absences: Mapped[int] = mapped_column(Integer, default=0)  
    employee_calls: Mapped[int] = mapped_column(Integer, default=0)  
    worker_type: Mapped[str] = mapped_column(String(50))  
    location: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[Date] = mapped_column(Date)  

    worker: Mapped[Worker] = relationship(back_populates='company')
