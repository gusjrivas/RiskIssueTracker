import uuid

from pydantic import BaseModel


class EntityStats(BaseModel):
    total: int
    # Claves de severidad "1".."9" como string (JSON no admite claves int),
    # siempre zero-filled para que el frontend no necesite defaults.
    by_severity: dict[str, int]
    by_status: dict[str, int]


class DashboardStatsResponse(BaseModel):
    risks: EntityStats
    issues: EntityStats


class SeverityItem(BaseModel):
    id: uuid.UUID
    title: str
    status: str


class SeverityItemsResponse(BaseModel):
    items: list[SeverityItem]
