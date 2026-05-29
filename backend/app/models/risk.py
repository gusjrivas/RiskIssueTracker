import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Uuid

from app.db.base import Base
from app.schemas.common import (
    ImpactLevel,
    ProbabilityLevel,
    Proximity,
    RiskCategory,
    RiskStatus,
)


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    category: Mapped[RiskCategory] = mapped_column(
        SAEnum(RiskCategory, native_enum=False), nullable=False, index=True
    )
    probability: Mapped[ProbabilityLevel] = mapped_column(
        SAEnum(ProbabilityLevel, native_enum=False), nullable=False
    )
    impact: Mapped[ImpactLevel] = mapped_column(
        SAEnum(ImpactLevel, native_enum=False), nullable=False
    )
    proximity: Mapped[Proximity] = mapped_column(
        SAEnum(Proximity, native_enum=False), nullable=False
    )
    severity: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[RiskStatus] = mapped_column(
        SAEnum(RiskStatus, native_enum=False),
        nullable=False,
        default=RiskStatus.open,
        index=True,
    )
    mitigation_strategy: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    contingency_plan: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    derived_issue_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey("issues.id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )
