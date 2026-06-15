import uuid

from pydantic import BaseModel

from app.schemas.common import EntityType


class EntityStats(BaseModel):
    total: int
    # Claves de severidad "1".."9" como string (JSON no admite claves int),
    # siempre zero-filled para que el frontend no necesite defaults.
    by_severity: dict[str, int]
    by_status: dict[str, int]


class DashboardStatsResponse(BaseModel):
    risks: EntityStats
    issues: EntityStats


class SeverityGroupItem(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    type: EntityType


class SeverityGroup(BaseModel):
    severity: int
    items: list[SeverityGroupItem]


class SeverityItemsGroupedResponse(BaseModel):
    groups: list[SeverityGroup]
