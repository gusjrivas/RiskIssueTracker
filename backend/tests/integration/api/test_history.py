import uuid

import pytest

from app.models.history_entry import HistoryEntry
from app.models.issue import Issue
from app.models.project import Project
from app.models.risk import Risk
from app.models.user import User
from app.schemas.common import (
    EntityType,
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
from app.services.severity_calculator import get_severity


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def regular_user(db):
    u = User(email="hist_user@example.com", full_name="Hist User",
             password_hash=hash_password("pass123"),
             role=UserRole.user, status=UserStatus.active)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def user_token(regular_user):
    return create_access_token(regular_user)


@pytest.fixture
def project(db, regular_user):
    p = Project(name="History Test Project", created_by=regular_user.id)
    db.add(p); db.commit(); db.refresh(p)
    return p


@pytest.fixture
def risk(db, project, regular_user):
    r = Risk(
        project_id=project.id,
        title="History Risk",
        category=RiskCategory.costos,
        probability=ProbabilityLevel.alta,
        impact=ImpactLevel.alto,
        proximity=Proximity.corto_plazo,
        severity=get_severity(ProbabilityLevel.alta, ImpactLevel.alto, Proximity.corto_plazo),
        status=RiskStatus.open,
        created_by=regular_user.id,
    )
    db.add(r); db.commit(); db.refresh(r)
    return r


@pytest.fixture
def issue(db, project, regular_user):
    i = Issue(
        project_id=project.id,
        title="History Issue",
        severity=3,
        status=IssueStatus.open,
        created_by=regular_user.id,
    )
    db.add(i); db.commit(); db.refresh(i)
    return i


@pytest.fixture
def risk_history_entry(db, risk, regular_user):
    e = HistoryEntry(
        entity_type=EntityType.risk,
        entity_id=risk.id,
        from_status="open",
        to_status="in_progress",
        changed_by=regular_user.id,
    )
    db.add(e); db.commit(); db.refresh(e)
    return e


# ---------------------------------------------------------------------------
# GET /history/{entity_type}/{entity_id}
# ---------------------------------------------------------------------------

class TestGetHistory:
    def test_authenticated_user_can_get_history(self, client, user_token, risk, risk_history_entry):
        resp = client.get(f"/api/v1/history/risk/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200

    def test_returns_pagination_structure(self, client, user_token, risk, risk_history_entry):
        resp = client.get(f"/api/v1/history/risk/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        assert all(k in body for k in ["items", "total", "page", "size", "pages"])

    def test_returns_entries_for_entity(self, client, user_token, risk, risk_history_entry):
        resp = client.get(f"/api/v1/history/risk/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert len(items) >= 1
        assert all(i["entity_id"] == str(risk.id) for i in items)

    def test_entry_has_expected_fields(self, client, user_token, risk, risk_history_entry):
        resp = client.get(f"/api/v1/history/risk/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        entry = resp.json()["items"][0]
        for field in ["id", "entity_type", "entity_id", "from_status",
                      "to_status", "changed_by", "created_at"]:
            assert field in entry

    def test_returns_empty_for_entity_with_no_history(self, client, user_token):
        resp = client.get(f"/api/v1/history/risk/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_without_token_returns_401(self, client, risk):
        resp = client.get(f"/api/v1/history/risk/{risk.id}")
        assert resp.status_code == 401

    def test_invalid_entity_type_returns_422(self, client, user_token):
        resp = client.get(f"/api/v1/history/unknown/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 422

    def test_issue_history_is_separate_from_risk_history(
        self, client, user_token, risk, issue, db, regular_user
    ):
        issue_entry = HistoryEntry(
            entity_type=EntityType.issue,
            entity_id=issue.id,
            from_status="open",
            to_status="in_progress",
            changed_by=regular_user.id,
        )
        risk_entry = HistoryEntry(
            entity_type=EntityType.risk,
            entity_id=risk.id,
            from_status="open",
            to_status="in_progress",
            changed_by=regular_user.id,
        )
        db.add(issue_entry); db.add(risk_entry); db.commit()

        resp_risk = client.get(f"/api/v1/history/risk/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        resp_issue = client.get(f"/api/v1/history/issue/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"})

        risk_ids = {i["entity_id"] for i in resp_risk.json()["items"]}
        issue_ids = {i["entity_id"] for i in resp_issue.json()["items"]}
        assert risk_ids.isdisjoint(issue_ids) or str(risk.id) not in issue_ids


# ---------------------------------------------------------------------------
# Integration: history recorded automatically on status transitions
# ---------------------------------------------------------------------------

class TestHistoryRecordedOnTransition:
    def test_risk_transition_creates_history_entry(self, client, user_token, risk):
        client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        resp = client.get(f"/api/v1/history/risk/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert len(items) >= 1
        latest = items[0]
        assert latest["to_status"] == "in_progress"
        assert latest["from_status"] == "open"

    def test_issue_transition_creates_history_entry(self, client, user_token, issue):
        client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        resp = client.get(f"/api/v1/history/issue/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert len(items) >= 1
        latest = items[0]
        assert latest["to_status"] == "in_progress"
        assert latest["from_status"] == "open"

    def test_multiple_transitions_accumulate_entries(self, client, user_token, risk):
        client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "closed"})
        resp = client.get(f"/api/v1/history/risk/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.json()["total"] == 2
