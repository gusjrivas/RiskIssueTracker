import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.common import PaginatedResponse


def log_action(
    db: Session,
    user_id: uuid.UUID | None,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID | None,
    changes: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    return entry


def list_audit_log(
    db: Session,
    user_id: uuid.UUID | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse:
    base_query = select(AuditLog).order_by(AuditLog.created_at.desc())
    if user_id is not None:
        base_query = base_query.where(AuditLog.user_id == user_id)
    if action is not None:
        base_query = base_query.where(AuditLog.action == action)
    if entity_type is not None:
        base_query = base_query.where(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        base_query = base_query.where(AuditLog.entity_id == entity_id)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.execute(count_query).scalar()

    items_query = base_query.offset((page - 1) * size).limit(size)
    items = db.execute(items_query).scalars().all()

    return PaginatedResponse.build(items=list(items), total=total, page=page, size=size)
