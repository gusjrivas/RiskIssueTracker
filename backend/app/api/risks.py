import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditEntryResponse
from app.schemas.common import PaginatedResponse, RiskCategory, RiskStatus
from app.schemas.risk import RiskCreate, RiskResponse, RiskStatusUpdate, RiskUpdate
from app.services import risk_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.post("", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
def create_risk(
    data: RiskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return risk_service.create_risk(db, data, current_user)


@router.get("", response_model=PaginatedResponse[RiskResponse])
def list_risks(
    project_id: uuid.UUID | None = Query(default=None),
    risk_status: RiskStatus | None = Query(default=None, alias="status"),
    category: RiskCategory | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return risk_service.list_risks(
        db,
        project_id=project_id,
        status=risk_status,
        category=category,
        page=page,
        size=size,
    )


@router.get("/{risk_id}/audit", response_model=PaginatedResponse[AuditEntryResponse])
def get_risk_audit(
    risk_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    risk_service.get_risk(db, risk_id)  # 404 if not found

    total = db.execute(
        select(func.count())
        .select_from(AuditLog)
        .where(AuditLog.entity_type == "risk")
        .where(AuditLog.entity_id == risk_id)
    ).scalar()

    rows = db.execute(
        select(AuditLog, User.full_name.label("editor_name"))
        .outerjoin(User, AuditLog.user_id == User.id)
        .where(AuditLog.entity_type == "risk")
        .where(AuditLog.entity_id == risk_id)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    items = [
        AuditEntryResponse(
            id=row.AuditLog.id,
            action=row.AuditLog.action,
            changes=row.AuditLog.changes,
            editor_name=row.editor_name,
            created_at=row.AuditLog.created_at,
        )
        for row in rows
    ]
    return PaginatedResponse.build(items=items, total=total, page=page, size=size)


@router.get("/{risk_id}", response_model=RiskResponse)
def get_risk(
    risk_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return risk_service.get_risk(db, risk_id)


@router.patch("/{risk_id}", response_model=RiskResponse)
def update_risk(
    risk_id: uuid.UUID,
    data: RiskUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return risk_service.update_risk(db, risk_id, data, current_user)


@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk(
    risk_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    risk_service.delete_risk(db, risk_id, current_user)


@router.patch("/{risk_id}/status", response_model=RiskResponse)
def transition_status(
    risk_id: uuid.UUID,
    data: RiskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return risk_service.transition_status(db, risk_id, data.status, current_user)


@router.patch("/{risk_id}/restore", response_model=RiskResponse)
def restore_risk(
    risk_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return risk_service.restore_risk(db, risk_id, current_user)
