import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
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


@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(
    issue_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return issue_service.get_issue(db, issue_id)


@router.put("/{issue_id}", response_model=IssueResponse)
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
