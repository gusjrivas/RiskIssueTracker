import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.risk import Risk
from app.models.user import User
from app.schemas.common import EntityType, IssueStatus, PaginatedResponse, RiskStatus, UserRole
from app.schemas.issue import IssueCreate, IssueUpdate

VALID_TRANSITIONS = frozenset(
    {
        (IssueStatus.open, IssueStatus.in_progress),
        (IssueStatus.in_progress, IssueStatus.closed),
    }
)


def _assert_can_modify(issue: Issue, current_user) -> None:
    is_creator = uuid.UUID(str(issue.created_by)) == uuid.UUID(str(current_user.id))
    is_owner = issue.owner_id and uuid.UUID(str(issue.owner_id)) == uuid.UUID(str(current_user.id))
    if not (is_creator or is_owner or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Sin permiso para modificar este issue")


def _assert_can_transition(issue: Issue, current_user) -> None:
    is_creator = uuid.UUID(str(issue.created_by)) == uuid.UUID(str(current_user.id))
    is_owner = issue.owner_id and uuid.UUID(str(issue.owner_id)) == uuid.UUID(
        str(current_user.id)
    )
    if not (is_creator or is_owner or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Sin permiso para cambiar el estado de este issue")


def _resolve_user_name(db: Session, user_id) -> str | None:
    if user_id is None:
        return None
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    return user.full_name if user else None


def get_issue(db: Session, issue_id: uuid.UUID) -> Issue:
    issue = db.execute(
        select(Issue).where(Issue.id == issue_id, Issue.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue no encontrado")
    return issue


def create_issue(db: Session, data: IssueCreate, current_user) -> Issue:
    issue = Issue(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=IssueStatus.open,
        mitigation_strategy=data.mitigation_strategy,
        contingency_plan=data.contingency_plan,
        owner_id=data.owner_id,
        created_by=current_user.id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    from app.services.audit_service import log_action
    changes = {"owner_name": _resolve_user_name(db, data.owner_id)} if data.owner_id else None
    log_action(db, user_id=current_user.id, action="create",
               entity_type="issue", entity_id=issue.id, changes=changes)

    return issue


def derive_from_risk(db: Session, risk_id: uuid.UUID, current_user) -> Issue:
    risk = db.execute(
        select(Risk).where(Risk.id == risk_id, Risk.deleted_at.is_(None))
    ).scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Riesgo no encontrado")

    is_creator = uuid.UUID(str(risk.created_by)) == uuid.UUID(str(current_user.id))
    is_owner = risk.owner_id and uuid.UUID(str(risk.owner_id)) == uuid.UUID(str(current_user.id))
    if not (is_creator or is_owner or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Sin permiso para derivar este riesgo")

    if risk.status != RiskStatus.in_progress:
        raise HTTPException(
            status_code=409,
            detail=f"El riesgo debe estar 'en progreso' para derivar un issue (estado actual: '{risk.status}')",
        )

    issue_id = uuid.uuid4()
    issue = Issue(
        id=issue_id,
        project_id=risk.project_id,
        risk_id=risk.id,
        title=risk.title,
        description=risk.description,
        severity=risk.severity,
        status=IssueStatus.open,
        created_by=current_user.id,
    )
    db.add(issue)
    db.flush()

    risk.status = RiskStatus.derived
    risk.derived_issue_id = issue_id

    db.commit()
    db.refresh(issue)

    from app.services.history_service import record_transition
    record_transition(
        db,
        entity_type=EntityType.risk,
        entity_id=risk.id,
        from_status=RiskStatus.in_progress,
        to_status=RiskStatus.derived,
        changed_by_id=current_user.id,
    )

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="derive",
               entity_type="issue", entity_id=issue.id,
               changes={"risk_id": str(risk.id)})

    return issue


def list_issues(
    db: Session,
    project_id: uuid.UUID | None = None,
    status: IssueStatus | None = None,
    risk_id: uuid.UUID | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse:
    base_query = select(Issue).where(Issue.deleted_at.is_(None))
    if project_id is not None:
        base_query = base_query.where(Issue.project_id == project_id)
    if status is not None:
        base_query = base_query.where(Issue.status == status)
    if risk_id is not None:
        base_query = base_query.where(Issue.risk_id == risk_id)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.execute(count_query).scalar()

    items_query = base_query.offset((page - 1) * size).limit(size)
    items = db.execute(items_query).scalars().all()

    return PaginatedResponse.build(items=list(items), total=total, page=page, size=size)


def update_issue(db: Session, issue_id: uuid.UUID, data: IssueUpdate, current_user) -> Issue:
    issue = get_issue(db, issue_id)
    _assert_can_modify(issue, current_user)

    update_dict = data.model_dump(exclude_unset=True)

    # Capture before/after for each changed field
    changes = {}
    owner_change = None

    for field, new_val in update_dict.items():
        old_val = getattr(issue, field)
        old_str = str(old_val) if old_val is not None else None
        new_str = str(new_val) if new_val is not None else None
        if old_str != new_str:
            if field == "owner_id":
                old_name = _resolve_user_name(db, old_val)
                new_name = _resolve_user_name(db, new_val)
                changes["owner"] = {
                    "from_id": old_str,
                    "from_name": old_name,
                    "to_id": new_str,
                    "to_name": new_name,
                }
                owner_change = changes["owner"]
            else:
                changes[field] = {"from": old_str, "to": new_str}
        setattr(issue, field, new_val)

    db.commit()
    db.refresh(issue)

    from app.services.audit_service import log_action
    if changes:
        log_action(db, user_id=current_user.id, action="update",
                   entity_type="issue", entity_id=issue.id, changes=changes)

    if owner_change is not None:
        log_action(db, user_id=current_user.id, action="owner_change",
                   entity_type="issue", entity_id=issue.id, changes=owner_change)

    return issue


def delete_issue(db: Session, issue_id: uuid.UUID, current_user) -> None:
    issue = get_issue(db, issue_id)
    _assert_can_modify(issue, current_user)
    from datetime import datetime, timezone
    issue.deleted_at = datetime.now(timezone.utc)
    db.commit()

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="delete",
               entity_type="issue", entity_id=issue.id)


def restore_issue(db: Session, issue_id: uuid.UUID, current_user) -> Issue:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden restaurar issues")
    issue = db.execute(select(Issue).where(Issue.id == issue_id)).scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue no encontrado")
    if issue.deleted_at is None:
        raise HTTPException(status_code=409, detail="El issue no está eliminado")
    issue.deleted_at = None
    db.commit()
    db.refresh(issue)

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="restore",
               entity_type="issue", entity_id=issue.id)
    return issue


def list_deleted_issues(db: Session, page: int = 1, size: int = 20) -> PaginatedResponse:
    base_query = select(Issue).where(Issue.deleted_at.is_not(None))
    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.execute(count_query).scalar()
    items = db.execute(base_query.offset((page - 1) * size).limit(size)).scalars().all()
    return PaginatedResponse.build(items=list(items), total=total, page=page, size=size)


def transition_status(
    db: Session, issue_id: uuid.UUID, new_status: IssueStatus, current_user
) -> Issue:
    issue = get_issue(db, issue_id)
    _assert_can_transition(issue, current_user)

    if (issue.status, new_status) not in VALID_TRANSITIONS:
        raise HTTPException(
            status_code=409,
            detail=f"Transición inválida de '{issue.status}' a '{new_status}'",
        )

    prev_status = issue.status
    issue.status = new_status
    db.commit()
    db.refresh(issue)

    from app.services.history_service import record_transition
    record_transition(
        db,
        entity_type=EntityType.issue,
        entity_id=issue.id,
        from_status=prev_status,
        to_status=new_status,
        changed_by_id=current_user.id,
    )

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="status_change",
               entity_type="issue", entity_id=issue.id,
               changes={"from": prev_status.value, "to": new_status.value})

    return issue
