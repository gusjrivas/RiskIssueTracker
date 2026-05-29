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
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_user(db):
    u = User(email="audit_admin@example.com", full_name="Audit Admin",
             password_hash=hash_password("admin123"),
             role=UserRole.admin, status=UserStatus.active)
    db.add(u); db.commit(); db.refresh(u)
    return u


@pytest.fixture
def regular_user(db):
    u = User(email="audit_user@example.com", full_name="Audit User",
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
def project(db, regular_user):
    p = Project(name="Audit Test Project", created_by=regular_user.id)
    db.add(p); db.commit(); db.refresh(p)
    return p


@pytest.fixture
def risk(db, project, regular_user):
    r = Risk(
        project_id=project.id,
        title="Audit Risk",
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


# ---------------------------------------------------------------------------
# GET /admin/audit-log
# ---------------------------------------------------------------------------

class TestGetAuditLog:
    def test_admin_can_access_audit_log(self, client, admin_token):
        resp = client.get("/api/v1/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    def test_regular_user_gets_403(self, client, user_token):
        resp = client.get("/api/v1/admin/audit-log",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

    def test_unauthenticated_gets_401(self, client):
        resp = client.get("/api/v1/admin/audit-log")
        assert resp.status_code == 401

    def test_returns_pagination_structure(self, client, admin_token):
        resp = client.get("/api/v1/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"})
        body = resp.json()
        assert all(k in body for k in ["items", "total", "page", "size", "pages"])

    def test_entry_has_expected_fields(self, client, admin_token, user_token, project):
        client.post("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Audited Project"})
        resp = client.get("/api/v1/admin/audit-log",
            headers={"Authorization": f"Bearer {admin_token}"})
        items = resp.json()["items"]
        assert len(items) >= 1
        entry = items[0]
        for field in ["id", "user_id", "action", "entity_type", "entity_id", "created_at"]:
            assert field in entry

    def test_filter_by_entity_type(self, client, admin_token, user_token, project):
        client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"project_id": str(project.id), "title": "R",
                  "category": "costos", "probability": "media",
                  "impact": "medio", "proximity": "mediano_plazo"})
        resp = client.get("/api/v1/admin/audit-log?entity_type=risk",
            headers={"Authorization": f"Bearer {admin_token}"})
        items = resp.json()["items"]
        assert all(i["entity_type"] == "risk" for i in items)

    def test_filter_by_action(self, client, admin_token, user_token, project):
        client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"project_id": str(project.id), "title": "R2",
                  "category": "costos", "probability": "baja",
                  "impact": "bajo", "proximity": "largo_plazo"})
        resp = client.get("/api/v1/admin/audit-log?action=create",
            headers={"Authorization": f"Bearer {admin_token}"})
        items = resp.json()["items"]
        assert all(i["action"] == "create" for i in items)

    def test_filter_by_user_id(self, client, admin_token, user_token, regular_user, project):
        client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"project_id": str(project.id), "title": "R3",
                  "category": "equipo", "probability": "baja",
                  "impact": "bajo", "proximity": "largo_plazo"})
        resp = client.get(f"/api/v1/admin/audit-log?user_id={regular_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        items = resp.json()["items"]
        assert all(i["user_id"] == str(regular_user.id) for i in items)


# ---------------------------------------------------------------------------
# Audit recorded automatically on mutations
# ---------------------------------------------------------------------------

class TestAuditRecordedOnMutations:
    def test_create_risk_is_audited(self, client, admin_token, user_token, project):
        client.post("/api/v1/risks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"project_id": str(project.id), "title": "Audited Risk",
                  "category": "costos", "probability": "media",
                  "impact": "medio", "proximity": "mediano_plazo"})
        resp = client.get("/api/v1/admin/audit-log?action=create&entity_type=risk",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.json()["total"] >= 1

    def test_update_risk_is_audited(self, client, admin_token, user_token, risk):
        client.put(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"title": "Updated Title"})
        resp = client.get("/api/v1/admin/audit-log?action=update&entity_type=risk",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.json()["total"] >= 1

    def test_delete_risk_is_audited(self, client, admin_token, user_token, risk):
        risk_id = str(risk.id)
        client.delete(f"/api/v1/risks/{risk.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        resp = client.get(f"/api/v1/admin/audit-log?action=delete&entity_type=risk",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.json()["total"] >= 1

    def test_risk_status_transition_is_audited(self, client, admin_token, user_token, risk):
        client.patch(f"/api/v1/risks/{risk.id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"status": "in_progress"})
        resp = client.get("/api/v1/admin/audit-log?action=status_change&entity_type=risk",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.json()["total"] >= 1

    def test_create_project_is_audited(self, client, admin_token, user_token):
        client.post("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Audited Project"})
        resp = client.get("/api/v1/admin/audit-log?action=create&entity_type=project",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.json()["total"] >= 1
