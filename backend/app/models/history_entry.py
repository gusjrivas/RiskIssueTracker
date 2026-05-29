import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Uuid

from app.db.base import Base
from app.schemas.common import EntityType


class HistoryEntry(Base):
    __tablename__ = "history_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid.uuid4
    )
    entity_type: Mapped[EntityType] = mapped_column(
        SAEnum(EntityType, native_enum=False), nullable=False, index=True
    )
    # No FK — entity_id can reference risks or issues from the same column
    entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False), nullable=False, index=True
    )
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False, index=True
    )
