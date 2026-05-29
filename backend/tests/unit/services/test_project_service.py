import uuid
from unittest.mock import MagicMock

import pytest

from app.schemas.common import UserRole, UserStatus


def _svc():
    from app.services import project_service
    return project_service


def _make_user(role=UserRole.user, user_id=None):
    from app.models.user import User
    u = User()
    u.id = user_id or uuid.uuid4()
    u.email = "user@example.com"
    u.full_name = "Test User"
    u.role = role
    u.status = UserStatus.active
    u.password_hash = "hashed"
    u.google_id = None
    return u


def _make_project(creator_id=None):
    from app.models.project import Project
    from datetime import datetime, timezone
    p = Project()
    p.id = uuid.uuid4()
    p.name = "Test Project"
    p.description = "A test project"
    p.client = "Client Inc"
    p.created_by = creator_id or uuid.uuid4()
    p.created_at = datetime.now(timezone.utc)
    p.updated_at = datetime.now(timezone.utc)
    return p


def _db_with(result):
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = result
    db.execute.return_value.scalars.return_value.all.return_value = [result] if result else []
    db.execute.return_value.scalar.return_value = 1 if result else 0
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


def _db_empty():
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.execute.return_value.scalars.return_value.all.return_value = []
    db.execute.return_value.scalar.return_value = 0
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class TestCreateProject:
    def test_create_returns_project_with_correct_fields(self):
        from app.schemas.project import ProjectCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)

        data = ProjectCreate(name="My Project", description="Desc", client="ACME")
        project = _svc().create_project(db, data, user)

        assert project.name == "My Project"
        assert project.description == "Desc"
        assert project.client == "ACME"

    def test_create_sets_created_by_from_current_user(self):
        from app.schemas.project import ProjectCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)

        data = ProjectCreate(name="My Project")
        project = _svc().create_project(db, data, user)

        assert uuid.UUID(str(project.created_by)) == uuid.UUID(str(user.id))

    def test_create_calls_db_add_and_commit(self):
        from app.schemas.project import ProjectCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)

        _svc().create_project(db, ProjectCreate(name="P"), user)

        assert db.add.call_count >= 1
        assert db.commit.call_count >= 1


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------

class TestGetProject:
    def test_get_existing_returns_project(self):
        project = _make_project()
        db = _db_with(project)
        result = _svc().get_project(db, project.id)
        assert result is project

    def test_get_nonexistent_raises_404(self):
        from fastapi import HTTPException
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().get_project(db, uuid.uuid4())
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class TestUpdateProject:
    def test_creator_can_update_own_project(self):
        from app.schemas.project import ProjectUpdate
        user = _make_user()
        project = _make_project(creator_id=user.id)
        db = _db_with(project)

        result = _svc().update_project(db, project.id, ProjectUpdate(name="New Name"), user)
        assert result.name == "New Name"

    def test_admin_can_update_any_project(self):
        from app.schemas.project import ProjectUpdate
        admin = _make_user(role=UserRole.admin)
        project = _make_project(creator_id=uuid.uuid4())  # different creator
        db = _db_with(project)

        result = _svc().update_project(db, project.id, ProjectUpdate(name="Admin Edit"), admin)
        assert result.name == "Admin Edit"

    def test_other_user_cannot_update_raises_403(self):
        from fastapi import HTTPException
        from app.schemas.project import ProjectUpdate
        user = _make_user()
        project = _make_project(creator_id=uuid.uuid4())  # someone else's project
        db = _db_with(project)

        with pytest.raises(HTTPException) as exc:
            _svc().update_project(db, project.id, ProjectUpdate(name="Hack"), user)
        assert exc.value.status_code == 403

    def test_update_nonexistent_raises_404(self):
        from fastapi import HTTPException
        from app.schemas.project import ProjectUpdate
        user = _make_user()
        db = _db_empty()

        with pytest.raises(HTTPException) as exc:
            _svc().update_project(db, uuid.uuid4(), ProjectUpdate(name="X"), user)
        assert exc.value.status_code == 404

    def test_partial_update_only_changes_provided_fields(self):
        from app.schemas.project import ProjectUpdate
        user = _make_user()
        project = _make_project(creator_id=user.id)
        project.description = "Original description"
        db = _db_with(project)

        _svc().update_project(db, project.id, ProjectUpdate(name="New Name"), user)
        assert project.description == "Original description"


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestDeleteProject:
    def test_creator_can_delete_own_project(self):
        user = _make_user()
        project = _make_project(creator_id=user.id)
        db = _db_with(project)

        _svc().delete_project(db, project.id, user)

        db.delete.assert_called_once_with(project)
        assert db.commit.call_count >= 1

    def test_admin_can_delete_any_project(self):
        admin = _make_user(role=UserRole.admin)
        project = _make_project(creator_id=uuid.uuid4())
        db = _db_with(project)

        _svc().delete_project(db, project.id, admin)
        db.delete.assert_called_once_with(project)

    def test_other_user_cannot_delete_raises_403(self):
        from fastapi import HTTPException
        user = _make_user()
        project = _make_project(creator_id=uuid.uuid4())
        db = _db_with(project)

        with pytest.raises(HTTPException) as exc:
            _svc().delete_project(db, project.id, user)
        assert exc.value.status_code == 403

    def test_delete_nonexistent_raises_404(self):
        from fastapi import HTTPException
        user = _make_user()
        db = _db_empty()

        with pytest.raises(HTTPException) as exc:
            _svc().delete_project(db, uuid.uuid4(), user)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

class TestListProjects:
    def test_list_returns_paginated_response(self):
        from app.schemas.project import ProjectResponse
        project = _make_project()
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 3
        db.execute.return_value.scalars.return_value.all.return_value = [project]

        result = _svc().list_projects(db, page=1, size=20)

        assert hasattr(result, "items")
        assert hasattr(result, "total")
        assert hasattr(result, "page")
        assert hasattr(result, "size")
        assert hasattr(result, "pages")

    def test_list_total_reflects_db_count(self):
        from app.schemas.project import ProjectResponse
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 7
        db.execute.return_value.scalars.return_value.all.return_value = []

        result = _svc().list_projects(db, page=1, size=20)
        assert result.total == 7
