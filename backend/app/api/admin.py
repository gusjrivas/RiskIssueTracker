import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.schemas.auth import UserResponse
from app.schemas.common import PaginatedResponse, UserStatus
from app.services import audit_service
from app.services.auth_service import require_admin

router = APIRouter()


@router.get("/users", response_model=PaginatedResponse[UserResponse])
def list_users(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_admin)] = None,
):
    total = db.execute(select(func.count()).select_from(User)).scalar()
    users = db.execute(select(User).offset((page - 1) * size).limit(size)).scalars().all()
    return PaginatedResponse[UserResponse](
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if size > 0 else 0,
    )


@router.patch("/users/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: Annotated[User, Depends(require_admin)] = None,
):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.active
    db.commit()
    db.refresh(user)

    from app.services.audit_service import log_action
    log_action(db, user_id=current_admin.id, action="approve_user",
               entity_type="user", entity_id=user.id)

    return user


@router.patch("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: Annotated[User, Depends(require_admin)] = None,
):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.inactive
    db.commit()
    db.refresh(user)

    from app.services.audit_service import log_action
    log_action(db, user_id=current_admin.id, action="deactivate_user",
               entity_type="user", entity_id=user.id)

    return user


@router.get("/audit-log", response_model=PaginatedResponse[AuditLogResponse])
def get_audit_log(
    user_id: uuid.UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    entity_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_admin)] = None,
):
    return audit_service.list_audit_log(
        db,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        page=page,
        size=size,
    )
