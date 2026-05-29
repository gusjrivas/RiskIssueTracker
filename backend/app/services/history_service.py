import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.history_entry import HistoryEntry
from app.schemas.common import EntityType, PaginatedResponse


def record_transition(
    db: Session,
    entity_type: EntityType,
    entity_id: uuid.UUID,
    from_status,
    to_status,
    changed_by_id: uuid.UUID,
    notes: str | None = None,
) -> HistoryEntry:
    entry = HistoryEntry(
        entity_type=entity_type,
        entity_id=entity_id,
        from_status=from_status.value if hasattr(from_status, "value") else from_status,
        to_status=to_status.value if hasattr(to_status, "value") else to_status,
        changed_by=changed_by_id,
        notes=notes,
    )
    db.add(entry)
    db.commit()
    return entry


def list_history(
    db: Session,
    entity_type: EntityType,
    entity_id: uuid.UUID,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse:
    base_query = (
        select(HistoryEntry)
        .where(HistoryEntry.entity_type == entity_type)
        .where(HistoryEntry.entity_id == entity_id)
        .order_by(HistoryEntry.created_at.desc())
    )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.execute(count_query).scalar()

    items_query = base_query.offset((page - 1) * size).limit(size)
    items = db.execute(items_query).scalars().all()

    return PaginatedResponse.build(items=list(items), total=total, page=page, size=size)
