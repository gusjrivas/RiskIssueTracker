import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import EntityType, PaginatedResponse
from app.schemas.history_entry import HistoryEntryResponse
from app.services import history_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/{entity_type}/{entity_id}", response_model=PaginatedResponse[HistoryEntryResponse])
def get_history(
    entity_type: EntityType,
    entity_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return history_service.list_history(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        page=page,
        size=size,
    )
