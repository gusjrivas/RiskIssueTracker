import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditEntryResponse
from app.schemas.common import IssueStatus, PaginatedResponse
from app.schemas.issue import IssueCreate, IssueDerive, IssueResponse, IssueStatusUpdate, IssueUpdate
from app.services import issue_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    data: IssueCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.create_issue(db, data, current_user)


@router.post("/derive", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def derive_issue(
    data: IssueDerive,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.derive_from_risk(db, data.risk_id, current_user)


@router.get("", response_model=PaginatedResponse[IssueResponse])
def list_issues(
    project_id: uuid.UUID | None = Query(default=None),
    issue_status: IssueStatus | None = Query(default=None, alias="status"),
    risk_id: uuid.UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.list_issues(
        db,
        project_id=project_id,
        status=issue_status,
        risk_id=risk_id,
        page=page,
        size=size,
    )


@router.get("/{issue_id}/audit", response_model=PaginatedResponse[AuditEntryResponse])
def get_issue_audit(
    issue_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    issue_service.get_issue(db, issue_id)  # 404 if not found

    total = db.execute(
        select(func.count())
        .select_from(AuditLog)
        .where(AuditLog.entity_type == "issue")
        .where(AuditLog.entity_id == issue_id)
    ).scalar()

    rows = db.execute(
        select(AuditLog, User.full_name.label("editor_name"))
        .outerjoin(User, AuditLog.user_id == User.id)
        .where(AuditLog.entity_type == "issue")
        .where(AuditLog.entity_id == issue_id)
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


@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.get_issue(db, issue_id)


@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: uuid.UUID,
    data: IssueUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.update_issue(db, issue_id, data, current_user)


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    issue_service.delete_issue(db, issue_id, current_user)


@router.patch("/{issue_id}/status", response_model=IssueResponse)
def transition_status(
    issue_id: uuid.UUID,
    data: IssueStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.transition_status(db, issue_id, data.status, current_user)


@router.patch("/{issue_id}/restore", response_model=IssueResponse)
def restore_issue(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.restore_issue(db, issue_id, current_user)
