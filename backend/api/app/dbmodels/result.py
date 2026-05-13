from __future__ import annotations

import uuid

from typing import TYPE_CHECKING, Optional

from datetime import date

from sqlalchemy import (
    ForeignKey,
    Date,
    UUID,
    Boolean,
    Numeric,
    Text,
    String
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .base import Base

if TYPE_CHECKING:
    from .area import Area
    from .groups import Group
    from .workers import Worker
    from .surveys import Surveys


class Result(Base):

    __tablename__ = 'result'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True
    )

    # Datos Métricos de la IA
    burnout_confidence: Mapped[float] = mapped_column(
        Numeric(10, 4)
    )

    burnout_class: Mapped[str] = mapped_column(
        String(50)      
    )

    flag: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    # Almacena las razones enviadas por la IA (Causas técnicas)
    burnout_reasons: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # La acción sugerida por el motor de reglas del Backend (Acción sugerida por la empresa)
    suggested_intervention: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    # Estado del flujo de RRHH: 'Pendiente', 'Aprobada', 'Rechazada', 'Ejecutada'
    intervention_status: Mapped[str] = mapped_column(
        String(50),
        default='Pendiente'
    )

    # Espacio para que RRHH deje comentarios al aprobar/rechazar
    hr_comment: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    id_worker: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('worker.id')
    )

    id_group: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('group.id')
    )

    id_area: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('area.id')
    )

    id_survey: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('survey.id')
    )

    generation_date: Mapped[date] = mapped_column(
        Date,
        default=date.today
    )

    workers: Mapped["Worker"] = relationship(
        back_populates='results'
    )

    survey: Mapped["Surveys"] = relationship(
        back_populates='results'
    )

    area: Mapped["Area"] = relationship(
        back_populates='results'
    )

    group: Mapped["Group"] = relationship(
        back_populates='results'
    )
