"""
Este módulo define el modelo de base de datos para los rangos (Ranks) del sistema.
Los rangos representan los niveles jerárquicos de los trabajadores. Cada rango tiene
un identificador único, un nombre descriptivo y un nivel numérico que determina los
permisos y el acceso a funcionalidades específicas del sistema. Los niveles son:
1 (comun) - Trabajador regular con acceso limitado a sus propios datos
2 (lider) - Líder de grupo con capacidad de gestionar su equipo
3 (rrhh) - Personal de recursos humanos con acceso administrativo completo
"""

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
    from .workers import Worker

    
class Rank(Base):
    
    __tablename__ = 'rank'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )
    
    rank_name: Mapped[str] = mapped_column(String(100))
    # Nivel numérico para control de acceso: 1=común, 2=líder, 3=RRHH
    level: Mapped[int] = mapped_column(Integer)

    workers: Mapped[list[Worker]]=relationship(back_populates='rank')