import math
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.schemas.common import PaginatedResponse, UserRole
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate


def _assert_can_modify(project: Project, current_user: User) -> None:
    is_creator = uuid.UUID(str(project.created_by)) == uuid.UUID(str(current_user.id))
    if not (is_creator or current_user.role == UserRole.admin):
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")


def create_project(db: Session, data: ProjectCreate, current_user: User) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        client=data.client,
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="create",
               entity_type="project", entity_id=project.id)

    return project


def list_projects(db: Session, page: int, size: int) -> PaginatedResponse[ProjectResponse]:
    total = db.execute(select(func.count()).select_from(Project)).scalar()
    items = db.execute(
        select(Project).offset((page - 1) * size).limit(size)
    ).scalars().all()
    return PaginatedResponse[ProjectResponse](
        items=[ProjectResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if size > 0 else 0,
    )


def get_project(db: Session, project_id: uuid.UUID) -> Project:
    project = db.execute(
        select(Project).where(Project.id == project_id)
    ).scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def update_project(
    db: Session, project_id: uuid.UUID, data: ProjectUpdate, current_user: User
) -> Project:
    project = get_project(db, project_id)
    _assert_can_modify(project, current_user)
    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="update",
               entity_type="project", entity_id=project.id, changes=update_dict)

    return project


def delete_project(db: Session, project_id: uuid.UUID, current_user: User) -> None:
    project = get_project(db, project_id)
    _assert_can_modify(project, current_user)
    project_id_copy = project.id
    db.delete(project)
    db.commit()

    from app.services.audit_service import log_action
    log_action(db, user_id=current_user.id, action="delete",
               entity_type="project", entity_id=project_id_copy)
