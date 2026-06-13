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


def _get_severity_items(client, token, severity, type_):
    return client.get(
        f"/api/v1/dashboard/stats/severity/{severity}?type={type_}",
        headers={"Authorization": f"Bearer {token}"},
    )


# ---------------------------------------------------------------------------
# GET /dashboard/stats/severity/{severity}
# ---------------------------------------------------------------------------

class TestSeverityItems:
    def test_requires_auth(self, client):
        resp = client.get("/api/v1/dashboard/stats/severity/1?type=risk")
        assert resp.status_code in (401, 403)

    def test_admin_sees_all_risks_for_severity(self, client, admin_token, seed):
        resp = _get_severity_items(client, admin_token, 1, "risk")
        assert resp.status_code == 200
        items = resp.json()["items"]
        # risk_a1 (open) + risk_a3 (open, owner=regular_user) — ambos severidad 1
        assert len(items) == 2
        assert {i["title"] for i in items} == {"Risk sev 1"}
        assert {i["status"] for i in items} == {"open"}

    def test_admin_sees_issue_for_severity(self, client, admin_token, seed):
        resp = _get_severity_items(client, admin_token, 9, "issue")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["title"] == "Issue sev 9"
        assert items[0]["status"] == "closed"

    def test_regular_user_sees_only_visible_risks(self, client, user_token, seed):
        # severidad 1: solo ve risk_a3 (es owner), no risk_a1 (de admin)
        resp = _get_severity_items(client, user_token, 1, "risk")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

        # severidad 4: ve risk_b1 porque project_b es propio (created_by)
        resp_b = _get_severity_items(client, user_token, 4, "risk")
        items_b = resp_b.json()["items"]
        assert len(items_b) == 1
        assert items_b[0]["status"] == "derived"

    def test_regular_user_does_not_see_others_issues(self, client, user_token, seed):
        # severidad 9 (issue_a1) pertenece al admin en project_a -> no visible
        resp = _get_severity_items(client, user_token, 9, "issue")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_severity_out_of_range_returns_422(self, client, admin_token):
        assert _get_severity_items(client, admin_token, 0, "risk").status_code == 422
        assert _get_severity_items(client, admin_token, 10, "risk").status_code == 422

    def test_invalid_type_returns_422(self, client, admin_token):
        resp = _get_severity_items(client, admin_token, 1, "foo")
        assert resp.status_code == 422

    def test_severity_without_items_returns_empty_list(self, client, admin_token, seed):
        resp = _get_severity_items(client, admin_token, 7, "risk")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_deleted_risk_excluded(self, client, admin_token, seed):
        # risk_a4 (severidad 2) tiene deleted_at seteado en el seed
        resp = _get_severity_items(client, admin_token, 2, "risk")
        assert resp.status_code == 200
        assert resp.json()["items"] == []
