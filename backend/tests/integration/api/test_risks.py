import uuid

import pytest

from app.models.project import Project
from app.models.risk import Risk
from app.models.user import User
from app.schemas.common import (
    ImpactLevel,
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
def other_user(db):
    u = User(email="other@example.com", full_name="Other",
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
    p = Project(name="Test Project", created_by=regular_user.id)
    db.add(p); db.commit(); db.refresh(p)
    return p


@pytest.fixture
def risk(db, project, regular_user):
    r = Risk(
        project_id=project.id,
        title="Test Risk",
        description="Risk desc",
        category=RiskCategory.costos,
        probability=ProbabilityLevel.media,
        impact=ImpactLevel.medio,
        proximity=Proximity.mediano_plazo,
        severity=get_severity(ProbabilityLevel.media, ImpactLevel.medio, Proximity.mediano_plazo),
        status=RiskStatus.open,
        created_by=regular_user.id,
    )
    db.add(r); db.commit(); db.refresh(r)
    return r


_VALID_RISK_BODY = {
    "title": "New Risk",
    "category": "costos",
    "probability": "media",
    "impact": "medio",
    "proximity": "mediano_plazo",
}


# ---------------------------------------------------------------------------
# POST /risks
# ---------------------------------------------------------------------------

class TestCreateRisk:
    def test_authenticated_user_can_create_risk(self, client, user_token, project):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_RISK_BODY, "project_id": str(project.id)})
        assert resp.status_code == 201

    def test_create_returns_severity_auto_calculated(self, client, user_token, project):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_RISK_BODY, "project_id": str(project.id)})
        body = resp.json()
        expected = get_severity(ProbabilityLevel.media, ImpactLevel.medio, Proximity.mediano_plazo)
        assert body["severity"] == expected

    def test_create_ignores_client_supplied_severity(self, client, user_token, project):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_RISK_BODY, "project_id": str(project.id), "severity": 99})
        body = resp.json()
        expected = get_severity(ProbabilityLevel.media, ImpactLevel.medio, Proximity.mediano_plazo)
        assert body["severity"] == expected

    def test_create_default_status_is_open(self, client, user_token, project):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_RISK_BODY, "project_id": str(project.id)})
        assert resp.json()["status"] == "open"

    def test_create_sets_created_by_to_current_user(self, client, user_token, project, regular_user):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_RISK_BODY, "project_id": str(project.id)})
        assert resp.json()["created_by"] == str(regular_user.id)

    def test_create_without_token_returns_401(self, client, project):
        resp = client.post("/api/v1/risks",
            json={**_VALID_RISK_BODY, "project_id": str(project.id)})
        assert resp.status_code == 401

    def test_create_missing_required_field_returns_422(self, client, user_token, project):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "No category"})
        assert resp.status_code == 422

    def test_create_invalid_enum_value_returns_422(self, client, user_token, project):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_RISK_BODY, "project_id": str(project.id),
                  "probability": "invalid_value"})
        assert resp.status_code == 422

    def test_create_with_optional_fields(self, client, user_token, project):
        resp = client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={**_VALID_RISK_BODY, "project_id": str(project.id),
                  "mitigation_strategy": "Plan A", "contingency_plan": "Plan B"})
        body = resp.json()
        assert body["mitigation_strategy"] == "Plan A"
        assert body["contingency_plan"] == "Plan B"


# ---------------------------------------------------------------------------
# GET /risks
# ---------------------------------------------------------------------------

class TestListRisks:
    def test_authenticated_user_can_list(self, client, user_token):
        resp = client.get("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200

    def test_list_without_token_returns_401(self, client):
        resp = client.get("/api/v1/risks")
        assert resp.status_code == 401

    def test_list_returns_pagination_structure(self, client, user_token):
        resp = client.get("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        assert all(k in body for k in ["items", "total", "page", "size", "pages"])

    def test_created_risk_appears_in_list(self, client, user_token, risk):
        resp = client.get("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"})
        ids = [r["id"] for r in resp.json()["items"]]
        assert str(risk.id) in ids

    def test_filter_by_project_id(self, client, user_token, risk, project, db, regular_user):
        other_project = Project(name="Other", created_by=regular_user.id)
        db.add(other_project); db.commit(); db.refresh(other_project)
        other_risk = Risk(
            project_id=other_project.id, title="Other Risk",
            category=RiskCategory.equipo,
            probability=ProbabilityLevel.baja, impact=ImpactLevel.bajo,
            proximity=Proximity.largo_plazo,
            severity=get_severity(ProbabilityLevel.baja, ImpactLevel.bajo, Proximity.largo_plazo),
            status=RiskStatus.open, created_by=regular_user.id,
        )
        db.add(other_risk); db.commit()
        resp = client.get(f"/api/v1/risks?project_id={project.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert all(r["project_id"] == str(project.id) for r in items)
        assert str(risk.id) in [r["id"] for r in items]

    def test_filter_by_status(self, client, user_token, risk, db, project, regular_user):
        closed_risk = Risk(
            project_id=project.id, title="Closed Risk",
            category=RiskCategory.costos,
            probability=ProbabilityLevel.baja, impact=ImpactLevel.bajo,
            proximity=Proximity.largo_plazo,
            severity=get_severity(ProbabilityLevel.baja, ImpactLevel.bajo, Proximity.largo_plazo),
            status=RiskStatus.closed, created_by=regular_user.id,
        )
        db.add(closed_risk); db.commit()
        resp = client.get("/api/v1/risks?status=closed",
            headers={"Authorization": f"Bearer {user_token}"})
        items = resp.json()["items"]
        assert all(r["status"] == "closed" for r in items)

    def test_list_page_size_params(self, client, user_token, risk):
        resp = client.get("/api/v1/risks?page=1&size=1",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        assert len(body["items"]) <= 1
        assert body["size"] == 1


# ---------------------------------------------------------------------------
# GET /risks/{id}
# ---------------------------------------------------------------------------

class TestGetRisk:
    def test_get_existing_returns_200(self, client, user_token, risk):
        resp = client.get(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == str(risk.id)

    def test_get_nonexistent_returns_404(self, client, user_token):
        resp = client.get(f"/api/v1/risks/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 404

    def test_get_without_token_returns_401(self, client, risk):
        resp = client.get(f"/api/v1/risks/{risk.id}")
        assert resp.status_code == 401

    def test_get_returns_all_expected_fields(self, client, user_token, risk):
        resp = client.get(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        for field in ["id", "project_id", "title", "category", "probability",
                      "impact", "proximity", "severity", "status",
                      "owner_id", "created_by", "created_at", "updated_at"]:
            assert field in body


# ---------------------------------------------------------------------------
# PUT /risks/{id}
# ---------------------------------------------------------------------------

class TestUpdateRisk:
    def test_creator_can_update_risk(self, client, user_token, risk):
        resp = client.put(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Updated Title"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"

    def test_admin_can_update_any_risk(self, client, admin_token, risk):
        resp = client.put(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"title": "Admin Updated"})
        assert resp.status_code == 200

    def test_other_user_cannot_update_returns_403(self, client, other_token, risk):
        resp = client.put(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"title": "Stolen"})
        assert resp.status_code == 403

    def test_update_without_token_returns_401(self, client, risk):
        resp = client.put(f"/api/v1/risks/{risk.id}", json={"title": "X"})
        assert resp.status_code == 401

    def test_update_nonexistent_returns_404(self, client, user_token):
        resp = client.put(f"/api/v1/risks/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "X"})
        assert resp.status_code == 404

    def test_update_probability_changes_severity(self, client, user_token, risk):
        # media+medio+mediano_plazo → exposure=0.10 → medio zone → severity=4
        # muy_alta+alto+mediano_plazo → exposure=0.36 → alto zone → severity=3
        old_severity = risk.severity
        resp = client.put(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"probability": "muy_alta", "impact": "alto"})
        new_severity = resp.json()["severity"]
        expected = get_severity(ProbabilityLevel.muy_alta, ImpactLevel.alto, risk.proximity)
        assert new_severity == expected
        assert new_severity != old_severity

    def test_update_title_does_not_change_severity(self, client, user_token, risk):
        old_severity = risk.severity
        resp = client.put(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "New Title Only"})
        assert resp.json()["severity"] == old_severity

    def test_partial_update_preserves_other_fields(self, client, user_token, risk):
        resp = client.put(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Only Title"})
        body = resp.json()
        assert body["category"] == risk.category.value
        assert body["description"] == risk.description


# ---------------------------------------------------------------------------
# DELETE /risks/{id}
# ---------------------------------------------------------------------------

class TestDeleteRisk:
    def test_creator_can_delete_risk(self, client, user_token, risk):
        resp = client.delete(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 204
        get_resp = client.get(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert get_resp.status_code == 404

    def test_admin_can_delete_any_risk(self, client, admin_token, risk):
        resp = client.delete(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 204

    def test_other_user_cannot_delete_returns_403(self, client, other_token, risk):
        resp = client.delete(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {other_token}"})
        assert resp.status_code == 403

    def test_delete_without_token_returns_401(self, client, risk):
        resp = client.delete(f"/api/v1/risks/{risk.id}")
        assert resp.status_code == 401

    def test_delete_nonexistent_returns_404(self, client, user_token):
        resp = client.delete(f"/api/v1/risks/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /risks/{id}/status
# ---------------------------------------------------------------------------

class TestStatusTransition:
    def test_creator_can_transition(self, client, user_token, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

    def test_admin_can_transition(self, client, admin_token, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 200

    def test_other_user_cannot_transition_returns_403(self, client, other_token, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 403

    def test_transition_without_token_returns_401(self, client, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            json={"status": "in_progress"})
        assert resp.status_code == 401

    def test_open_to_in_progress_valid(self, client, user_token, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        assert resp.json()["status"] == "in_progress"

    def test_in_progress_to_closed_valid(self, client, user_token, risk, db):
        risk.status = RiskStatus.in_progress
        db.commit()
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "closed"})
        assert resp.json()["status"] == "closed"

    def test_in_progress_to_derived_valid(self, client, user_token, risk, db):
        risk.status = RiskStatus.in_progress
        db.commit()
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "derived"})
        assert resp.json()["status"] == "derived"

    def test_open_to_closed_invalid_returns_409(self, client, user_token, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "closed"})
        assert resp.status_code == 409

    def test_open_to_derived_invalid_returns_409(self, client, user_token, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "derived"})
        assert resp.status_code == 409

    def test_closed_to_anything_returns_409(self, client, user_token, risk, db):
        risk.status = RiskStatus.closed
        db.commit()
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "open"})
        assert resp.status_code == 409

    def test_derived_to_anything_returns_409(self, client, user_token, risk, db):
        risk.status = RiskStatus.derived
        db.commit()
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "closed"})
        assert resp.status_code == 409

    def test_transition_nonexistent_risk_returns_404(self, client, user_token):
        resp = client.patch(f"/api/v1/risks/{uuid.uuid4()}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        assert resp.status_code == 404

    def test_transition_invalid_status_value_returns_422(self, client, user_token, risk):
        resp = client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "nonexistent"})
        assert resp.status_code == 422
