import uuid

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
from app.services.severity_calculator import get_severity


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_user(db):
    u = User(email="admin_i@example.com", full_name="Admin",
             password_hash=hash_password("admin123"),
             role=UserRole.admin, status=UserStatus.active)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def regular_user(db):
    u = User(email="regular_i@example.com", full_name="Regular",
             password_hash=hash_password("pass123"),
             role=UserRole.user, status=UserStatus.active)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def other_user(db):
    u = User(email="other_i@example.com", full_name="Other",
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


@pytest.fixture
def other_token(other_user):
    return create_access_token(other_user)


@pytest.fixture
def project(db, regular_user):
    p = Project(name="Issue Test Project", created_by=regular_user.id)
    db.add(p); db.commit(); db.refresh(p)
    return p


@pytest.fixture
def risk(db, project, regular_user):
    r = Risk(
        project_id=project.id,
        title="Risk for derivation",
        category=RiskCategory.costos,
        probability=ProbabilityLevel.alta,
        impact=ImpactLevel.alto,
        proximity=Proximity.corto_plazo,
        severity=get_severity(ProbabilityLevel.alta, ImpactLevel.alto, Proximity.corto_plazo),
        status=RiskStatus.in_progress,
        created_by=regular_user.id,
    )
    db.add(r); db.commit(); db.refresh(r)
    return r


@pytest.fixture
def issue(db, project, regular_user):
    i = Issue(
        project_id=project.id,
        title="Test Issue",
        description="Issue desc",
        severity=3,
        status=IssueStatus.open,
        created_by=regular_user.id,
    )
    db.add(i); db.commit(); db.refresh(i)
    return i


_VALID_ISSUE_BODY = {
    "title": "New Issue",
    "severity": 3,
}


# ---------------------------------------------------------------------------
# POST /issues
# ---------------------------------------------------------------------------

class TestCreateIssue:
    def test_authenticated_user_can_create_issue(self, client, user_token, project):
        resp = client.post("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_ISSUE_BODY, "project_id": str(project.id)})
        assert resp.status_code == 201

    def test_create_returns_correct_fields(self, client, user_token, project):
        resp = client.post("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_ISSUE_BODY, "project_id": str(project.id)})
        body = resp.json()
        assert body["title"] == "New Issue"
        assert body["severity"] == 3
        assert body["status"] == "open"

    def test_create_sets_created_by_to_current_user(self, client, user_token, project, regular_user):
        resp = client.post("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_ISSUE_BODY, "project_id": str(project.id)})
        assert resp.json()["created_by"] == str(regular_user.id)

    def test_create_risk_id_is_null_for_standalone(self, client, user_token, project):
        resp = client.post("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_ISSUE_BODY, "project_id": str(project.id)})
        assert resp.json()["risk_id"] is None

    def test_create_without_token_returns_401(self, client, project):
        resp = client.post("/api/v1/issues",
            json={**_VALID_ISSUE_BODY, "project_id": str(project.id)})
        assert resp.status_code == 401

    def test_create_missing_required_field_returns_422(self, client, user_token):
        resp = client.post("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "No severity or project_id"})
        assert resp.status_code == 422

    def test_create_severity_out_of_range_returns_422(self, client, user_token, project):
        resp = client.post("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_ISSUE_BODY, "project_id": str(project.id), "severity": 10})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /issues/derive
# ---------------------------------------------------------------------------

class TestDeriveIssue:
    def test_derive_creates_issue_from_risk(self, client, user_token, risk):
        resp = client.post("/api/v1/issues/derive",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"risk_id": str(risk.id)})
        assert resp.status_code == 201

    def test_derive_copies_title_and_severity_from_risk(self, client, user_token, risk):
        resp = client.post("/api/v1/issues/derive",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"risk_id": str(risk.id)})
        body = resp.json()
        assert body["title"] == risk.title
        assert body["severity"] == risk.severity

    def test_derive_links_issue_to_risk(self, client, user_token, risk):
        resp = client.post("/api/v1/issues/derive",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"risk_id": str(risk.id)})
        assert resp.json()["risk_id"] == str(risk.id)

    def test_derive_transitions_risk_to_derived(self, client, user_token, risk, db):
        client.post("/api/v1/issues/derive",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"risk_id": str(risk.id)})
        db.refresh(risk)
        assert risk.status == RiskStatus.derived

    def test_derive_sets_risk_derived_issue_id(self, client, user_token, risk, db):
        resp = client.post("/api/v1/issues/derive",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"risk_id": str(risk.id)})
        issue_id = resp.json()["id"]
        db.refresh(risk)
        assert str(risk.derived_issue_id) == issue_id

    def test_derive_risk_not_in_progress_returns_409(self, client, user_token, db, project, regular_user):
        open_risk = Risk(
            project_id=project.id, title="Open Risk",
            category=RiskCategory.equipo,
            probability=ProbabilityLevel.baja, impact=ImpactLevel.bajo,
            proximity=Proximity.largo_plazo,
            severity=get_severity(ProbabilityLevel.baja, ImpactLevel.bajo, Proximity.largo_plazo),
            status=RiskStatus.open, created_by=regular_user.id,
        )
        db.add(open_risk); db.commit()
        resp = client.post("/api/v1/issues/derive",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"risk_id": str(open_risk.id)})
        assert resp.status_code == 409

    def test_derive_nonexistent_risk_returns_404(self, client, user_token):
        resp = client.post("/api/v1/issues/derive",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"risk_id": str(uuid.uuid4())})
        assert resp.status_code == 404

    def test_derive_without_token_returns_401(self, client, risk):
        resp = client.post("/api/v1/issues/derive",
            json={"risk_id": str(risk.id)})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /issues
# ---------------------------------------------------------------------------

class TestListIssues:
    def test_authenticated_user_can_list(self, client, user_token):
        resp = client.get("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200

    def test_list_without_token_returns_401(self, client):
        resp = client.get("/api/v1/issues")
        assert resp.status_code == 401

    def test_list_returns_pagination_structure(self, client, user_token):
        resp = client.get("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        assert all(k in body for k in ["items", "total", "page", "size", "pages"])

    def test_created_issue_appears_in_list(self, client, user_token, issue):
        resp = client.get("/api/v1/issues",
            headers={"Authorization": f"Bearer {user_token}"})
        ids = [i["id"] for i in resp.json()["items"]]
        assert str(issue.id) in ids

    def test_filter_by_project_id(self, client, user_token, issue, project, db, regular_user):
        other_project = Project(name="Other", created_by=regular_user.id)
        db.add(other_project); db.commit(); db.refresh(other_project)
        other_issue = Issue(
            project_id=other_project.id, title="Other Issue",
            severity=5, status=IssueStatus.open, created_by=regular_user.id,
        )
        db.add(other_issue); db.commit()
        resp = client.get(f"/api/v1/issues?project_id={project.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert all(i["project_id"] == str(project.id) for i in items)

    def test_filter_by_status(self, client, user_token, issue, db, project, regular_user):
        closed_issue = Issue(
            project_id=project.id, title="Closed Issue",
            severity=4, status=IssueStatus.closed, created_by=regular_user.id,
        )
        db.add(closed_issue); db.commit()
        resp = client.get("/api/v1/issues?status=closed",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert all(i["status"] == "closed" for i in items)

    def test_filter_by_risk_id(self, client, user_token, risk, db, project, regular_user):
        linked_issue = Issue(
            project_id=project.id, title="Linked Issue",
            risk_id=risk.id, severity=2,
            status=IssueStatus.open, created_by=regular_user.id,
        )
        db.add(linked_issue); db.commit()
        resp = client.get(f"/api/v1/issues?risk_id={risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert all(i["risk_id"] == str(risk.id) for i in items)


# ---------------------------------------------------------------------------
# GET /issues/{id}
# ---------------------------------------------------------------------------

class TestGetIssue:
    def test_get_existing_returns_200(self, client, user_token, issue):
        resp = client.get(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == str(issue.id)

    def test_get_nonexistent_returns_404(self, client, user_token):
        resp = client.get(f"/api/v1/issues/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 404

    def test_get_without_token_returns_401(self, client, issue):
        resp = client.get(f"/api/v1/issues/{issue.id}")
        assert resp.status_code == 401

    def test_get_returns_all_expected_fields(self, client, user_token, issue):
        resp = client.get(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        for field in ["id", "project_id", "risk_id", "title", "severity",
                      "status", "owner_id", "created_by", "created_at", "updated_at"]:
            assert field in body


# ---------------------------------------------------------------------------
# PUT /issues/{id}
# ---------------------------------------------------------------------------

class TestUpdateIssue:
    def test_creator_can_update_issue(self, client, user_token, issue):
        resp = client.put(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Updated Title"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"

    def test_admin_can_update_any_issue(self, client, admin_token, issue):
        resp = client.put(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "Admin Updated"})
        assert resp.status_code == 200

    def test_other_user_cannot_update_returns_403(self, client, other_token, issue):
        resp = client.put(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"title": "Stolen"})
        assert resp.status_code == 403

    def test_update_without_token_returns_401(self, client, issue):
        resp = client.put(f"/api/v1/issues/{issue.id}", json={"title": "X"})
        assert resp.status_code == 401

    def test_update_nonexistent_returns_404(self, client, user_token):
        resp = client.put(f"/api/v1/issues/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "X"})
        assert resp.status_code == 404

    def test_partial_update_preserves_other_fields(self, client, user_token, issue):
        resp = client.put(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Only Title"})
        body = resp.json()
        assert body["severity"] == issue.severity
        assert body["description"] == issue.description


# ---------------------------------------------------------------------------
# DELETE /issues/{id}
# ---------------------------------------------------------------------------

class TestDeleteIssue:
    def test_creator_can_delete_issue(self, client, user_token, issue):
        resp = client.delete(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 204
        get_resp = client.get(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert get_resp.status_code == 404

    def test_admin_can_delete_any_issue(self, client, admin_token, issue):
        resp = client.delete(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 204

    def test_other_user_cannot_delete_returns_403(self, client, other_token, issue):
        resp = client.delete(f"/api/v1/issues/{issue.id}",
            headers={"Authorization": f"Bearer {other_token}"})
        assert resp.status_code == 403

    def test_delete_without_token_returns_401(self, client, issue):
        resp = client.delete(f"/api/v1/issues/{issue.id}")
        assert resp.status_code == 401

    def test_delete_nonexistent_returns_404(self, client, user_token):
        resp = client.delete(f"/api/v1/issues/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /issues/{id}/status
# ---------------------------------------------------------------------------

class TestStatusTransition:
    def test_creator_can_transition(self, client, user_token, issue):
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_admin_can_transition(self, client, admin_token, issue):
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 200

    def test_other_user_cannot_transition_returns_403(self, client, other_token, issue):
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 403

    def test_transition_without_token_returns_401(self, client, issue):
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            json={"status": "in_progress"})
        assert resp.status_code == 401

    def test_open_to_in_progress_valid(self, client, user_token, issue):
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        assert resp.json()["status"] == "in_progress"

    def test_in_progress_to_closed_valid(self, client, user_token, issue, db):
        issue.status = IssueStatus.in_progress
        db.commit()
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "closed"})
        assert resp.json()["status"] == "closed"

    def test_open_to_closed_invalid_returns_409(self, client, user_token, issue):
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "closed"})
        assert resp.status_code == 409

    def test_closed_to_anything_returns_409(self, client, user_token, issue, db):
        issue.status = IssueStatus.closed
        db.commit()
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "open"})
        assert resp.status_code == 409

    def test_transition_nonexistent_issue_returns_404(self, client, user_token):
        resp = client.patch(f"/api/v1/issues/{uuid.uuid4()}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 404

    def test_transition_invalid_status_value_returns_422(self, client, user_token, issue):
        resp = client.patch(f"/api/v1/issues/{issue.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "nonexistent"})
        assert resp.status_code == 422
