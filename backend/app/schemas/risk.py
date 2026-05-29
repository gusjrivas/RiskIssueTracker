import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.common import (
    ImpactLevel,
    ProbabilityLevel,
    Proximity,
    RiskCategory,
    RiskStatus,
)


class RiskCreate(BaseModel):
    project_id: uuid.UUID
    title: str
    description: str | None = None
    category: RiskCategory
    probability: ProbabilityLevel
    impact: ImpactLevel
    proximity: Proximity
    mitigation_strategy: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None


class RiskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: RiskCategory | None = None
    probability: ProbabilityLevel | None = None
    impact: ImpactLevel | None = None
    proximity: Proximity | None = None
    mitigation_strategy: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None


class RiskStatusUpdate(BaseModel):
    status: RiskStatus


class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None = None
    category: RiskCategory
    probability: ProbabilityLevel
    impact: ImpactLevel
    proximity: Proximity
    severity: int
    status: RiskStatus
    mitigation_strategy: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
