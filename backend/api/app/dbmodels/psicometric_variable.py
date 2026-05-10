from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class PsicometricVariable(Base):
    __tablename__ = 'psicometric_variable'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)