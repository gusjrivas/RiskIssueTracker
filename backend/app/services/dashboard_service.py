from enum import Enum

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.project import Project
from app.models.risk import Risk
from app.models.user import User
from app.schemas.common import EntityType, IssueStatus, RiskStatus, UserRole
from app.schemas.dashboard import (
    DashboardStatsResponse,
    EntityStats,
    SeverityGroup,
    SeverityGroupItem,
    SeverityItemsGroupedResponse,
)


def _visibility_clause(model, current_user: User):
    """Filtro de visibilidad: admin ve todo (None); un user ve las entidades
    donde es owner o creador, o que pertenecen a proyectos creados por él."""
    if current_user.role == UserRole.admin:
        return None
    own_projects = select(Project.id).where(Project.created_by == current_user.id)
    return or_(
        model.owner_id == current_user.id,
        model.created_by == current_user.id,
        model.project_id.in_(own_projects),
    )


def _entity_stats(
    db: Session, model, status_enum: type[Enum], current_user: User
) -> EntityStats:
    conditions = [model.deleted_at.is_(None)]
    visibility = _visibility_clause(model, current_user)
    if visibility is not None:
        conditions.append(visibility)

    severity_rows = db.execute(
        select(model.severity, func.count())
        .where(*conditions)
        .group_by(model.severity)
    ).all()
    status_rows = db.execute(
        select(model.status, func.count())
        .where(*conditions)
        .group_by(model.status)
    ).all()

    by_severity = {str(s): 0 for s in range(1, 10)}
    for severity, count in severity_rows:
        by_severity[str(severity)] = count

    by_status = {s.value: 0 for s in status_enum}
    for status, count in status_rows:
        key = status.value if isinstance(status, Enum) else str(status)
        by_status[key] = count

    return EntityStats(
        total=sum(by_severity.values()),
        by_severity=by_severity,
        by_status=by_status,
    )


def get_stats(db: Session, current_user: User) -> DashboardStatsResponse:
    return DashboardStatsResponse(
        risks=_entity_stats(db, Risk, RiskStatus, current_user),
        issues=_entity_stats(db, Issue, IssueStatus, current_user),
    )


def get_severity_groups(db: Session, current_user: User) -> SeverityItemsGroupedResponse:
    groups: list[SeverityGroup] = []

    for severity in range(1, 10):
        items: list[SeverityGroupItem] = []

        for model, entity_type in ((Risk, EntityType.risk), (Issue, EntityType.issue)):
            conditions = [model.deleted_at.is_(None), model.severity == severity]
            visibility = _visibility_clause(model, current_user)
            if visibility is not None:
                conditions.append(visibility)

            rows = db.execute(
                select(model.id, model.title, model.status)
                .where(*conditions)
                .order_by(model.title)
            ).all()

            items.extend(
                SeverityGroupItem(
                    id=row.id, title=row.title, status=row.status.value, type=entity_type
                )
                for row in rows
            )

        if items:
            groups.append(SeverityGroup(severity=severity, items=items))

    return SeverityItemsGroupedResponse(groups=groups)
