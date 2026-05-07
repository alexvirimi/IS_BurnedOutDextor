
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    ForeignKey,
    UUID
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .workers import Worker

class AuthUser(Base):
    __tablename__ = 'auth_user'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    # Referencia al trabajador asociado a este usuario
    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('worker.id'),
        unique=True
    )
    # Nombre de usuario único para acceso
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # Contraseña en texto plano (como se requirió, sin hashing)
    password: Mapped[str] = mapped_column(String(100))

    # Relación hacia el trabajador
    worker: Mapped[Worker] = relationship()
