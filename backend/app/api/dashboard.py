from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import EntityType
from app.schemas.dashboard import DashboardStatsResponse, SeverityItemsResponse
from app.services import dashboard_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_stats(db, current_user)


@router.get("/stats/severity/{severity}", response_model=SeverityItemsResponse)
def get_severity_items(
    severity: int = Path(ge=1, le=9),
    entity_type: Literal[EntityType.risk, EntityType.issue] = Query(..., alias="type"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_severity_items(db, severity, entity_type, current_user)
