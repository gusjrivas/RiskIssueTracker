import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.schemas.common import EntityType, PaginatedResponse, RiskStatus, UserRole
from app.schemas.risk import RiskCreate, RiskUpdate
from app.services.severity_calculator import get_severity

VALID_TRANSITIONS = frozenset(
    {
        (RiskStatus.open, RiskStatus.in_progress),
        (RiskStatus.in_progress, RiskStatus.closed),
        (RiskStatus.in_progress, RiskStatus.derived),
    }
)

_SEVERITY_FIELDS = {"probability", "impact", "proximity"}


def _assert_can_modify(risk: Risk, current_user) -> None:
    is_creator = uuid.UUID(str(risk.created_by)) == uuid.UUID(str(current_user.id))
    if not (is_creator or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Not authorized to modify this risk")


def _assert_can_transition(risk: Risk, current_user) -> None:
    is_creator = uuid.UUID(str(risk.created_by)) == uuid.UUID(str(current_user.id))
    is_owner = risk.owner_id and uuid.UUID(str(risk.owner_id)) == uuid.UUID(
        str(current_user.id)
    )
    if not (is_creator or is_owner or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Not authorized to transition this risk")


def get_risk(db: Session, risk_id: uuid.UUID) -> Risk:
    risk = db.execute(select(Risk).where(Risk.id == risk_id)).scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


def create_risk(db: Session, data: RiskCreate, current_user) -> Risk:
    severity = get_severity(data.probability, data.impact, data.proximity)
    risk = Risk(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        category=data.category,
        probability=data.probability,
        impact=data.impact,
        proximity=data.proximity,
        severity=severity,
        status=RiskStatus.open,
        mitigation_strategy=data.mitigation_strategy,
        contingency_plan=data.contingency_plan,
        owner_id=data.owner_id,
        created_by=current_user.id,
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="create",
               entity_type="risk", entity_id=risk.id)

    return risk


def list_risks(
    db: Session,
    project_id: uuid.UUID | None = None,
    status: RiskStatus | None = None,
    category=None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse:
    base_query = select(Risk)
    if project_id is not None:
        base_query = base_query.where(Risk.project_id == project_id)
    if status is not None:
        base_query = base_query.where(Risk.status == status)
    if category is not None:
        base_query = base_query.where(Risk.category == category)

    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.execute(count_query).scalar()

    items_query = base_query.offset((page - 1) * size).limit(size)
    items = db.execute(items_query).scalars().all()

    return PaginatedResponse.build(items=list(items), total=total, page=page, size=size)


def update_risk(db: Session, risk_id: uuid.UUID, data: RiskUpdate, current_user) -> Risk:
    risk = get_risk(db, risk_id)
    _assert_can_modify(risk, current_user)

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(risk, field, value)

    if _SEVERITY_FIELDS & update_dict.keys():
        risk.severity = get_severity(risk.probability, risk.impact, risk.proximity)

    db.commit()
    db.refresh(risk)

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="update",
               entity_type="risk", entity_id=risk.id, changes=update_dict)

    return risk


def delete_risk(db: Session, risk_id: uuid.UUID, current_user) -> None:
    risk = get_risk(db, risk_id)
    _assert_can_modify(risk, current_user)
    risk_id_copy = risk.id
    db.delete(risk)
    db.commit()

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="delete",
               entity_type="risk", entity_id=risk_id_copy)


def transition_status(
    db: Session, risk_id: uuid.UUID, new_status: RiskStatus, current_user
) -> Risk:
    risk = get_risk(db, risk_id)
    _assert_can_transition(risk, current_user)

    if (risk.status, new_status) not in VALID_TRANSITIONS:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid transition from '{risk.status}' to '{new_status}'",
        )

    prev_status = risk.status
    risk.status = new_status
    db.commit()
    db.refresh(risk)

    from app.services.history_service import record_transition
    record_transition(
        db,
        entity_type=EntityType.risk,
        entity_id=risk.id,
        from_status=prev_status,
        to_status=new_status,
        changed_by_id=current_user.id,
    )

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="status_change",
               entity_type="risk", entity_id=risk.id,
               changes={"from": prev_status.value, "to": new_status.value})

    return risk
