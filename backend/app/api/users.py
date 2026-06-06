import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserBasic
from app.schemas.common import PaginatedResponse, UserStatus
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserBasic])
def list_active_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Returns active users — used for owner selection in risks and issues."""
    base_q = select(User).where(User.status == UserStatus.active).order_by(User.full_name)
    total = db.execute(
        select(func.count()).select_from(base_q.subquery())
    ).scalar()
    users = db.execute(base_q.offset((page - 1) * size).limit(size)).scalars().all()
    return PaginatedResponse[UserBasic](
        items=[UserBasic.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if size > 0 else 0,
    )
