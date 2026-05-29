import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
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


@router.get("/{risk_id}", response_model=RiskResponse)
def get_risk(
    risk_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return risk_service.get_risk(db, risk_id)


@router.put("/{risk_id}", response_model=RiskResponse)
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
