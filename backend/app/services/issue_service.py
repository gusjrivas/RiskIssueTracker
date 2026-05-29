import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.risk import Risk
from app.schemas.common import IssueStatus, PaginatedResponse, RiskStatus, UserRole
from app.schemas.issue import IssueCreate, IssueUpdate

VALID_TRANSITIONS = frozenset(
    {
        (IssueStatus.open, IssueStatus.in_progress),
        (IssueStatus.in_progress, IssueStatus.closed),
    }
)


def _assert_can_modify(issue: Issue, current_user) -> None:
    is_creator = uuid.UUID(str(issue.created_by)) == uuid.UUID(str(current_user.id))
    if not (is_creator or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Not authorized to modify this issue")


def _assert_can_transition(issue: Issue, current_user) -> None:
    is_creator = uuid.UUID(str(issue.created_by)) == uuid.UUID(str(current_user.id))
    is_owner = issue.owner_id and uuid.UUID(str(issue.owner_id)) == uuid.UUID(
        str(current_user.id)
    )
    if not (is_creator or is_owner or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Not authorized to transition this issue")


def get_issue(db: Session, issue_id: uuid.UUID) -> Issue:
    issue = db.execute(select(Issue).where(Issue.id == issue_id)).scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
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
    return issue


def derive_from_risk(db: Session, risk_id: uuid.UUID, current_user) -> Issue:
    risk = db.execute(select(Risk).where(Risk.id == risk_id)).scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    if risk.status != RiskStatus.in_progress:
        raise HTTPException(
            status_code=409,
            detail=f"Risk must be 'in_progress' to derive an issue, current status: '{risk.status}'",
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
    return issue


def list_issues(
    db: Session,
    project_id: uuid.UUID | None = None,
    status: IssueStatus | None = None,
    risk_id: uuid.UUID | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse:
    base_query = select(Issue)
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

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)
    return issue


def delete_issue(db: Session, issue_id: uuid.UUID, current_user) -> None:
    issue = get_issue(db, issue_id)
    _assert_can_modify(issue, current_user)
    db.delete(issue)
    db.commit()


def transition_status(
    db: Session, issue_id: uuid.UUID, new_status: IssueStatus, current_user
) -> Issue:
    issue = get_issue(db, issue_id)
    _assert_can_transition(issue, current_user)

    if (issue.status, new_status) not in VALID_TRANSITIONS:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid transition from '{issue.status}' to '{new_status}'",
        )

    issue.status = new_status
    db.commit()
    db.refresh(issue)
    return issue
