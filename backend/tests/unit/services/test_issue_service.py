import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.schemas.common import (
    ImpactLevel,
    IssueStatus,
    ProbabilityLevel,
    Proximity,
    RiskCategory,
    RiskStatus,
    UserRole,
    UserStatus,
)
from app.services.severity_calculator import get_severity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _svc():
    from app.services import issue_service
    return issue_service


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


def _make_risk(creator_id=None, status=RiskStatus.in_progress,
               probability=ProbabilityLevel.alta, impact=ImpactLevel.alto,
               proximity=Proximity.corto_plazo):
    from app.models.risk import Risk
    r = Risk()
    r.id = uuid.uuid4()
    r.project_id = uuid.uuid4()
    r.title = "Test Risk"
    r.description = "A test risk"
    r.category = RiskCategory.costos
    r.probability = probability
    r.impact = impact
    r.proximity = proximity
    r.severity = get_severity(probability, impact, proximity)
    r.status = status
    r.mitigation_strategy = None
    r.contingency_plan = None
    r.owner_id = None
    r.derived_issue_id = None
    r.created_by = creator_id or uuid.uuid4()
    r.created_at = datetime.now(timezone.utc)
    r.updated_at = datetime.now(timezone.utc)
    return r


def _make_issue(creator_id=None, owner_id=None, risk_id=None,
                status=IssueStatus.open, severity=3):
    from app.models.issue import Issue
    i = Issue()
    i.id = uuid.uuid4()
    i.project_id = uuid.uuid4()
    i.risk_id = risk_id
    i.owner_id = owner_id
    i.created_by = creator_id or uuid.uuid4()
    i.title = "Test Issue"
    i.description = "An issue"
    i.severity = severity
    i.status = status
    i.mitigation_strategy = None
    i.contingency_plan = None
    i.created_at = datetime.now(timezone.utc)
    i.updated_at = datetime.now(timezone.utc)
    return i


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


def _db_with_both(issue, risk):
    """Mock DB que devuelve issue para queries de Issue y risk para queries de Risk."""
    db = MagicMock()
    call_count = {"n": 0}

    def scalar_one_or_none():
        call_count["n"] += 1
        if call_count["n"] == 1:
            return risk
        return issue

    db.execute.return_value.scalar_one_or_none.side_effect = scalar_one_or_none
    db.execute.return_value.scalars.return_value.all.return_value = [issue]
    db.execute.return_value.scalar.return_value = 1
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


# ---------------------------------------------------------------------------
# Create standalone
# ---------------------------------------------------------------------------

class TestCreateIssue:
    def test_create_returns_issue_with_correct_fields(self):
        from app.schemas.issue import IssueCreate
        user = _make_user()
        db = _db_empty()
        data = IssueCreate(
            project_id=uuid.uuid4(),
            title="New Issue",
            severity=3,
        )
        issue = _svc().create_issue(db, data, user)
        assert issue.title == "New Issue"
        assert issue.severity == 3

    def test_create_sets_created_by_from_current_user(self):
        from app.schemas.issue import IssueCreate
        user = _make_user()
        db = _db_empty()
        data = IssueCreate(
            project_id=uuid.uuid4(),
            title="Issue",
            severity=5,
        )
        issue = _svc().create_issue(db, data, user)
        assert uuid.UUID(str(issue.created_by)) == uuid.UUID(str(user.id))

    def test_create_default_status_is_open(self):
        from app.schemas.issue import IssueCreate
        user = _make_user()
        db = _db_empty()
        data = IssueCreate(project_id=uuid.uuid4(), title="I", severity=4)
        issue = _svc().create_issue(db, data, user)
        assert issue.status == IssueStatus.open

    def test_create_calls_db_add_and_commit(self):
        from app.schemas.issue import IssueCreate
        user = _make_user()
        db = _db_empty()
        data = IssueCreate(project_id=uuid.uuid4(), title="I", severity=4)
        _svc().create_issue(db, data, user)
        assert db.add.call_count >= 1
        assert db.commit.call_count >= 1

    def test_create_risk_id_is_none_for_standalone(self):
        from app.schemas.issue import IssueCreate
        user = _make_user()
        db = _db_empty()
        data = IssueCreate(project_id=uuid.uuid4(), title="I", severity=4)
        issue = _svc().create_issue(db, data, user)
        assert issue.risk_id is None


# ---------------------------------------------------------------------------
# Derive from risk
# ---------------------------------------------------------------------------

class TestDeriveFromRisk:
    def test_derive_creates_issue_linked_to_risk(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        issue = _svc().derive_from_risk(db, risk.id, user)
        assert uuid.UUID(str(issue.risk_id)) == uuid.UUID(str(risk.id))

    def test_derive_copies_title_from_risk(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        risk.title = "Specific Risk Title"
        db = _db_with(risk)
        issue = _svc().derive_from_risk(db, risk.id, user)
        assert issue.title == "Specific Risk Title"

    def test_derive_copies_severity_from_risk(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        issue = _svc().derive_from_risk(db, risk.id, user)
        assert issue.severity == risk.severity

    def test_derive_copies_project_id_from_risk(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        issue = _svc().derive_from_risk(db, risk.id, user)
        assert uuid.UUID(str(issue.project_id)) == uuid.UUID(str(risk.project_id))

    def test_derive_transitions_risk_to_derived(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        _svc().derive_from_risk(db, risk.id, user)
        assert risk.status == RiskStatus.derived

    def test_derive_sets_risk_derived_issue_id(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        issue = _svc().derive_from_risk(db, risk.id, user)
        assert uuid.UUID(str(risk.derived_issue_id)) == uuid.UUID(str(issue.id))

    def test_derive_raises_404_if_risk_not_found(self):
        from fastapi import HTTPException
        user = _make_user()
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().derive_from_risk(db, uuid.uuid4(), user)
        assert exc.value.status_code == 404

    def test_derive_raises_409_if_risk_not_in_progress(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.open)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().derive_from_risk(db, risk.id, user)
        assert exc.value.status_code == 409

    def test_derive_raises_409_if_risk_already_derived(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.derived)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().derive_from_risk(db, risk.id, user)
        assert exc.value.status_code == 409

    def test_derive_issue_status_is_open(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        issue = _svc().derive_from_risk(db, risk.id, user)
        assert issue.status == IssueStatus.open


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------

class TestGetIssue:
    def test_get_existing_returns_issue(self):
        issue = _make_issue()
        db = _db_with(issue)
        result = _svc().get_issue(db, issue.id)
        assert result is issue

    def test_get_nonexistent_raises_404(self):
        from fastapi import HTTPException
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().get_issue(db, uuid.uuid4())
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class TestUpdateIssue:
    def test_creator_can_update_own_issue(self):
        from app.schemas.issue import IssueUpdate
        user = _make_user()
        issue = _make_issue(creator_id=user.id)
        db = _db_with(issue)
        result = _svc().update_issue(db, issue.id, IssueUpdate(title="New Title"), user)
        assert result.title == "New Title"

    def test_admin_can_update_any_issue(self):
        from app.schemas.issue import IssueUpdate
        admin = _make_user(role=UserRole.admin)
        issue = _make_issue(creator_id=uuid.uuid4())
        db = _db_with(issue)
        result = _svc().update_issue(db, issue.id, IssueUpdate(title="Admin Edit"), admin)
        assert result.title == "Admin Edit"

    def test_other_user_cannot_update_raises_403(self):
        from fastapi import HTTPException
        from app.schemas.issue import IssueUpdate
        user = _make_user()
        issue = _make_issue(creator_id=uuid.uuid4())
        db = _db_with(issue)
        with pytest.raises(HTTPException) as exc:
            _svc().update_issue(db, issue.id, IssueUpdate(title="Hack"), user)
        assert exc.value.status_code == 403

    def test_update_nonexistent_raises_404(self):
        from fastapi import HTTPException
        from app.schemas.issue import IssueUpdate
        user = _make_user()
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().update_issue(db, uuid.uuid4(), IssueUpdate(title="X"), user)
        assert exc.value.status_code == 404

    def test_partial_update_leaves_other_fields_unchanged(self):
        from app.schemas.issue import IssueUpdate
        user = _make_user()
        issue = _make_issue(creator_id=user.id)
        issue.description = "Original description"
        db = _db_with(issue)
        _svc().update_issue(db, issue.id, IssueUpdate(title="New Title"), user)
        assert issue.description == "Original description"

    def test_update_severity_manually(self):
        from app.schemas.issue import IssueUpdate
        user = _make_user()
        issue = _make_issue(creator_id=user.id, severity=5)
        db = _db_with(issue)
        _svc().update_issue(db, issue.id, IssueUpdate(severity=2), user)
        assert issue.severity == 2


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestDeleteIssue:
    def test_creator_can_delete_own_issue(self):
        user = _make_user()
        issue = _make_issue(creator_id=user.id)
        db = _db_with(issue)
        _svc().delete_issue(db, issue.id, user)
        db.delete.assert_called_once_with(issue)
        assert db.commit.call_count >= 1

    def test_admin_can_delete_any_issue(self):
        admin = _make_user(role=UserRole.admin)
        issue = _make_issue(creator_id=uuid.uuid4())
        db = _db_with(issue)
        _svc().delete_issue(db, issue.id, admin)
        db.delete.assert_called_once_with(issue)

    def test_other_user_cannot_delete_raises_403(self):
        from fastapi import HTTPException
        user = _make_user()
        issue = _make_issue(creator_id=uuid.uuid4())
        db = _db_with(issue)
        with pytest.raises(HTTPException) as exc:
            _svc().delete_issue(db, issue.id, user)
        assert exc.value.status_code == 403

    def test_delete_nonexistent_raises_404(self):
        from fastapi import HTTPException
        user = _make_user()
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().delete_issue(db, uuid.uuid4(), user)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

class TestTransitionStatus:
    def test_creator_can_transition(self):
        user = _make_user()
        issue = _make_issue(creator_id=user.id, status=IssueStatus.open)
        db = _db_with(issue)
        result = _svc().transition_status(db, issue.id, IssueStatus.in_progress, user)
        assert result.status == IssueStatus.in_progress

    def test_owner_can_transition(self):
        owner = _make_user()
        issue = _make_issue(owner_id=owner.id, status=IssueStatus.open)
        db = _db_with(issue)
        result = _svc().transition_status(db, issue.id, IssueStatus.in_progress, owner)
        assert result.status == IssueStatus.in_progress

    def test_admin_can_transition_any_issue(self):
        admin = _make_user(role=UserRole.admin)
        issue = _make_issue(creator_id=uuid.uuid4(), status=IssueStatus.open)
        db = _db_with(issue)
        result = _svc().transition_status(db, issue.id, IssueStatus.in_progress, admin)
        assert result.status == IssueStatus.in_progress

    def test_other_user_cannot_transition_raises_403(self):
        from fastapi import HTTPException
        user = _make_user()
        issue = _make_issue(creator_id=uuid.uuid4(), owner_id=uuid.uuid4(),
                            status=IssueStatus.open)
        db = _db_with(issue)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, issue.id, IssueStatus.in_progress, user)
        assert exc.value.status_code == 403

    def test_open_to_in_progress_valid(self):
        user = _make_user()
        issue = _make_issue(creator_id=user.id, status=IssueStatus.open)
        db = _db_with(issue)
        result = _svc().transition_status(db, issue.id, IssueStatus.in_progress, user)
        assert result.status == IssueStatus.in_progress

    def test_in_progress_to_closed_valid(self):
        user = _make_user()
        issue = _make_issue(creator_id=user.id, status=IssueStatus.in_progress)
        db = _db_with(issue)
        result = _svc().transition_status(db, issue.id, IssueStatus.closed, user)
        assert result.status == IssueStatus.closed

    def test_open_to_closed_invalid_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        issue = _make_issue(creator_id=user.id, status=IssueStatus.open)
        db = _db_with(issue)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, issue.id, IssueStatus.closed, user)
        assert exc.value.status_code == 409

    def test_closed_is_terminal_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        issue = _make_issue(creator_id=user.id, status=IssueStatus.closed)
        db = _db_with(issue)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, issue.id, IssueStatus.open, user)
        assert exc.value.status_code == 409

    def test_same_status_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        issue = _make_issue(creator_id=user.id, status=IssueStatus.open)
        db = _db_with(issue)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, issue.id, IssueStatus.open, user)
        assert exc.value.status_code == 409

    def test_transition_nonexistent_raises_404(self):
        from fastapi import HTTPException
        user = _make_user()
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, uuid.uuid4(), IssueStatus.in_progress, user)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

class TestListIssues:
    def test_list_returns_paginated_response(self):
        issue = _make_issue()
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 1
        db.execute.return_value.scalars.return_value.all.return_value = [issue]
        result = _svc().list_issues(db, page=1, size=20)
        for key in ("items", "total", "page", "size", "pages"):
            assert hasattr(result, key)

    def test_list_total_reflects_db_count(self):
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 7
        db.execute.return_value.scalars.return_value.all.return_value = []
        result = _svc().list_issues(db, page=1, size=20)
        assert result.total == 7
