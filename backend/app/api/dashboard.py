from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardStatsResponse, SeverityItemsGroupedResponse
from app.services import dashboard_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_stats(db, current_user)


@router.get("/stats/severity-items", response_model=SeverityItemsGroupedResponse)
def get_severity_items_grouped(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_severity_groups(db, current_user)
