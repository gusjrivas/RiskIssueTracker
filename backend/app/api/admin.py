import math
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.common import PaginatedResponse, UserStatus
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
    _: Annotated[User, Depends(require_admin)] = None,
):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.active
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: Annotated[User, Depends(require_admin)] = None,
):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = UserStatus.inactive
    db.commit()
    db.refresh(user)
    return user
