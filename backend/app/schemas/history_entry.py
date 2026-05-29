import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import EntityType


class HistoryEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_type: EntityType
    entity_id: uuid.UUID
    from_status: str | None = None
    to_status: str
    changed_by: uuid.UUID | None = None
    notes: str | None = None
    created_at: datetime
