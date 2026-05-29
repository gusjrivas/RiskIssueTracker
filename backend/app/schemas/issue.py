import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import IssueStatus


class IssueCreate(BaseModel):
    project_id: uuid.UUID
    title: str
    description: str | None = None
    severity: int = Field(..., ge=1, le=9)
    mitigation_strategy: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None


class IssueDerive(BaseModel):
    risk_id: uuid.UUID


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: int | None = Field(default=None, ge=1, le=9)
    mitigation_strategy: str | None = None
    contingency_plan: str | None = None
    owner_id: uuid.UUID | None = None


class IssueStatusUpdate(BaseModel):
    status: IssueStatus


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    risk_id: uuid.UUID | None = None
    owner_id: uuid.UUID | None = None
    created_by: uuid.UUID
    title: str
    description: str | None = None
    severity: int
    status: IssueStatus
    mitigation_strategy: str | None = None
    contingency_plan: str | None = None
    created_at: datetime
    updated_at: datetime
