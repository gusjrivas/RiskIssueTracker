from datetime import datetime, timezone

import pytest

from app.models.issue import Issue
from app.models.project import Project
from app.models.risk import Risk
from app.models.user import User
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
from app.services.auth_service import create_access_token, hash_password


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_user(db):
    u = User(email="admin@example.com", full_name="Admin",
             password_hash=hash_password("admin123"),
             role=UserRole.admin, status=UserStatus.active)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def regular_user(db):
    u = User(email="regular@example.com", full_name="Regular",
             password_hash=hash_password("pass123"),
             role=UserRole.user, status=UserStatus.active)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(admin_user)


@pytest.fixture
def user_token(regular_user):
    return create_access_token(regular_user)


def _make_risk(project, created_by, severity, status, owner_id=None, deleted_at=None):
    return Risk(
        project_id=project.id,
        title=f"Risk sev {severity}",
        category=RiskCategory.costos,
        probability=ProbabilityLevel.media,
        impact=ImpactLevel.medio,
        proximity=Proximity.mediano_plazo,
        severity=severity,
        status=status,
        created_by=created_by.id,
        owner_id=owner_id.id if owner_id else None,
        deleted_at=deleted_at,
    )


def _make_issue(project, created_by, severity, status, owner_id=None):
    return Issue(
        project_id=project.id,
        title=f"Issue sev {severity}",
        severity=severity,
        status=status,
        created_by=created_by.id,
        owner_id=owner_id.id if owner_id else None,
    )


@pytest.fixture
def seed(db, admin_user, regular_user):
    """Proyecto A (de admin) + Proyecto B (de regular_user) con datos mixtos.

    Visible para regular_user: risk_a3 (owner), issue_a2 (creador),
    risk_b1 e issue_b1 (proyecto B creado por él). El resto solo admin.
    """
    project_a = Project(name="Project A", created_by=admin_user.id)
    project_b = Project(name="Project B", created_by=regular_user.id)
    db.add_all([project_a, project_b]); db.commit()
    db.refresh(project_a); db.refresh(project_b)

    rows = [
        _make_risk(project_a, admin_user, 1, RiskStatus.open),
        _make_risk(project_a, admin_user, 5, RiskStatus.in_progress),
        _make_risk(project_a, admin_user, 1, RiskStatus.open, owner_id=regular_user),
        _make_risk(project_a, admin_user, 2, RiskStatus.open,
                   deleted_at=datetime.now(timezone.utc)),
        _make_risk(project_b, admin_user, 4, RiskStatus.derived),
        _make_issue(project_a, admin_user, 9, IssueStatus.closed),
        _make_issue(project_a, regular_user, 3, IssueStatus.open),
        _make_issue(project_b, admin_user, 4, IssueStatus.in_progress),
    ]
    db.add_all(rows); db.commit()
    return {"project_a": project_a, "project_b": project_b}


def _get_stats(client, token):
    return client.get("/api/v1/dashboard/stats",
                      headers={"Authorization": f"Bearer {token}"})


# ---------------------------------------------------------------------------
# GET /dashboard/stats
# ---------------------------------------------------------------------------

class TestDashboardStats:
    def test_requires_auth(self, client):
        resp = client.get("/api/v1/dashboard/stats")
        assert resp.status_code in (401, 403)

    def test_admin_sees_all_counts(self, client, admin_token, seed):
        resp = _get_stats(client, admin_token)
        assert resp.status_code == 200
        body = resp.json()

        assert body["risks"]["total"] == 4  # excluye el soft-deleted
        assert body["risks"]["by_severity"]["1"] == 2
        assert body["risks"]["by_severity"]["5"] == 1
        assert body["risks"]["by_severity"]["4"] == 1
        assert body["risks"]["by_status"] == {
            "open": 2, "in_progress": 1, "closed": 0, "derived": 1,
        }

        assert body["issues"]["total"] == 3
        assert body["issues"]["by_severity"]["9"] == 1
        assert body["issues"]["by_severity"]["3"] == 1
        assert body["issues"]["by_severity"]["4"] == 1
        assert body["issues"]["by_status"] == {
            "open": 1, "in_progress": 1, "closed": 1,
        }

    def test_regular_user_sees_only_visible(self, client, user_token, seed):
        resp = _get_stats(client, user_token)
        assert resp.status_code == 200
        body = resp.json()

        # risk_a3 (owner) + risk_b1 (proyecto propio)
        assert body["risks"]["total"] == 2
        assert body["risks"]["by_severity"]["1"] == 1
        assert body["risks"]["by_severity"]["4"] == 1
        assert body["risks"]["by_severity"]["5"] == 0
        assert body["risks"]["by_status"]["open"] == 1
        assert body["risks"]["by_status"]["derived"] == 1

        # issue_a2 (creador) + issue_b1 (proyecto propio)
        assert body["issues"]["total"] == 2
        assert body["issues"]["by_severity"]["3"] == 1
        assert body["issues"]["by_severity"]["4"] == 1
        assert body["issues"]["by_severity"]["9"] == 0

    def test_zero_filled_severities_and_statuses(self, client, admin_token, seed):
        body = _get_stats(client, admin_token).json()
        assert set(body["risks"]["by_severity"].keys()) == {str(s) for s in range(1, 10)}
        assert set(body["issues"]["by_severity"].keys()) == {str(s) for s in range(1, 10)}
        assert set(body["risks"]["by_status"].keys()) == {
            "open", "in_progress", "closed", "derived",
        }
        assert set(body["issues"]["by_status"].keys()) == {
            "open", "in_progress", "closed",
        }

    def test_totals_consistent(self, client, admin_token, seed):
        body = _get_stats(client, admin_token).json()
        for entity in ("risks", "issues"):
            stats = body[entity]
            assert stats["total"] == sum(stats["by_severity"].values())
            assert stats["total"] == sum(stats["by_status"].values())

    def test_empty_db_returns_zeroes(self, client, admin_token):
        body = _get_stats(client, admin_token).json()
        assert body["risks"]["total"] == 0
        assert body["issues"]["total"] == 0
        assert all(v == 0 for v in body["risks"]["by_severity"].values())
