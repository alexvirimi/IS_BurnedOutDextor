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
    from .groups import Group
    from .ranks import Rank
    from .identity_mapping import IdentityMapping
    from .company import Company


class Worker(Base):
    __tablename__ = 'worker'

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        default=uuid.uuid4,
        init=False
    )
    name: Mapped[str] = mapped_column(String(100))
    last_names: Mapped[str] = mapped_column(String(150))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(20))  # Demographics for survey analysis

    id_group: Mapped[uuid.UUID] = mapped_column(
        String(36), 
        ForeignKey('group.id')
    )
    id_rank: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('rank.id')
    )

    group: Mapped[Group] = relationship(back_populates='workers')
    group_leader: Mapped[Group] = relationship(back_populates='worker_leader')
    rank: Mapped[Rank] = relationship(back_populates='workers')
    mapping: Mapped[IdentityMapping] = relationship(back_populates='workers')
    company: Mapped[Company] = relationship(back_populates='worker')
