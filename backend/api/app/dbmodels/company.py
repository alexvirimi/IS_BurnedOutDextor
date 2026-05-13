from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
import enum
from sqlalchemy import (
    String, 
    Integer,
    Date,
    ForeignKey,
    UUID,
    Enum,
    CheckConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .workers import Worker


class WorkerTypeEnum(str, enum.Enum):
    """Worker type enum - restricted to Hibrida and Remota"""
    HIBRIDO = "Hibrida"
    REMOTO = "Remota"


class Company(Base):
    __tablename__ = 'company'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    id_worker: Mapped[uuid.UUID] = mapped_column(        
        UUID(as_uuid=True),
        ForeignKey('worker.id'),
        unique=True
    )  # One company record per worker    
    
    assigned_tasks: Mapped[int] = mapped_column(Integer, default=0)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0)
    absences: Mapped[int] = mapped_column(Integer, default=0)  
    employee_calls: Mapped[int] = mapped_column(Integer, default=0)  
    worker_type: Mapped[str] = mapped_column(
        Enum(WorkerTypeEnum, native_enum=False),
        nullable=False
    )  
    location: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[Date] = mapped_column(Date)  

    __table_args__ = (
        CheckConstraint(
            'completed_tasks <= assigned_tasks',
            name='ck_company_completed_le_assigned'
        ),
    )

    worker: Mapped[Worker] = relationship(back_populates='company')
