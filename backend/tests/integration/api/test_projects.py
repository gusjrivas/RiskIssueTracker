import uuid

import pytest

from app.models.project import Project
from app.models.user import User
from app.schemas.common import UserRole, UserStatus
from app.services.auth_service import create_access_token, hash_password


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_user(db):
    user = User(email="admin@example.com", full_name="Admin",
                password_hash=hash_password("admin123"),
                role=UserRole.admin, status=UserStatus.active)
    db.add(user); db.commit(); db.refresh(user)
    return user


@pytest.fixture
def regular_user(db):
    user = User(email="regular@example.com", full_name="Regular",
                password_hash=hash_password("pass123"),
                role=UserRole.user, status=UserStatus.active)
    db.add(user); db.commit(); db.refresh(user)
    return user


@pytest.fixture
def other_user(db):
    user = User(email="other@example.com", full_name="Other",
                password_hash=hash_password("pass123"),
                role=UserRole.user, status=UserStatus.active)
    db.add(user); db.commit(); db.refresh(user)
    return user


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
    p = Project(name="Alpha Project", description="Test desc",
                client="ACME Corp", created_by=regular_user.id)
    db.add(p); db.commit(); db.refresh(p)
    return p


# ---------------------------------------------------------------------------
# POST /projects
# ---------------------------------------------------------------------------

class TestCreateProject:
    def test_authenticated_user_can_create_project(self, client, user_token):
        resp = client.post("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "New Project"})
        assert resp.status_code == 201

    def test_create_returns_project_fields(self, client, user_token, regular_user):
        resp = client.post("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "My Project", "description": "Desc", "client": "ACME"})
        body = resp.json()
        assert body["name"] == "My Project"
        assert body["description"] == "Desc"
        assert body["client"] == "ACME"
        assert "id" in body
        assert "created_at" in body

    def test_create_sets_created_by_to_current_user(self, client, user_token, regular_user):
        resp = client.post("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Owned Project"})
        assert resp.json()["created_by"] == str(regular_user.id)

    def test_create_without_token_returns_401(self, client):
        resp = client.post("/api/v1/projects", json={"name": "P"})
        assert resp.status_code == 401

    def test_create_without_name_returns_422(self, client, user_token):
        resp = client.post("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"description": "no name"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /projects
# ---------------------------------------------------------------------------

class TestListProjects:
    def test_authenticated_user_can_list(self, client, user_token):
        resp = client.get("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200

    def test_list_without_token_returns_401(self, client):
        resp = client.get("/api/v1/projects")
        assert resp.status_code == 401

    def test_list_returns_pagination_fields(self, client, user_token):
        resp = client.get("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        assert all(k in body for k in ["items", "total", "page", "size", "pages"])

    def test_list_page_size_params(self, client, user_token, project):
        resp = client.get("/api/v1/projects?page=1&size=1",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        assert len(body["items"]) <= 1
        assert body["size"] == 1

    def test_created_project_appears_in_list(self, client, user_token, project):
        resp = client.get("/api/v1/projects",
            headers={"Authorization": f"Bearer {user_token}"})
        ids = [item["id"] for item in resp.json()["items"]]
        assert str(project.id) in ids


# ---------------------------------------------------------------------------
# GET /projects/{id}
# ---------------------------------------------------------------------------

class TestGetProject:
    def test_get_existing_returns_200(self, client, user_token, project):
        resp = client.get(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == str(project.id)

    def test_get_nonexistent_returns_404(self, client, user_token):
        resp = client.get(f"/api/v1/projects/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 404

    def test_get_without_token_returns_401(self, client, project):
        resp = client.get(f"/api/v1/projects/{project.id}")
        assert resp.status_code == 401

    def test_get_returns_all_expected_fields(self, client, user_token, project):
        resp = client.get(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        body = resp.json()
        for field in ["id", "name", "description", "client", "created_by", "created_at", "updated_at"]:
            assert field in body


# ---------------------------------------------------------------------------
# PUT /projects/{id}
# ---------------------------------------------------------------------------

class TestUpdateProject:
    def test_creator_can_update_own_project(self, client, user_token, project):
        resp = client.put(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_admin_can_update_any_project(self, client, admin_token, project):
        resp = client.put(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Admin Updated"})
        assert resp.status_code == 200

    def test_other_user_cannot_update_returns_403(self, client, other_token, project):
        resp = client.put(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"name": "Stolen"})
        assert resp.status_code == 403

    def test_update_without_token_returns_401(self, client, project):
        resp = client.put(f"/api/v1/projects/{project.id}", json={"name": "X"})
        assert resp.status_code == 401

    def test_update_nonexistent_returns_404(self, client, user_token):
        resp = client.put(f"/api/v1/projects/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "X"})
        assert resp.status_code == 404

    def test_partial_update_leaves_other_fields_unchanged(self, client, user_token, project):
        resp = client.put(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"name": "Only Name Changed"})
        body = resp.json()
        assert body["description"] == project.description
        assert body["client"] == project.client


# ---------------------------------------------------------------------------
# DELETE /projects/{id}
# ---------------------------------------------------------------------------

class TestDeleteProject:
    def test_creator_can_delete_own_project(self, client, user_token, project):
        resp = client.delete(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 204
        get_resp = client.get(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert get_resp.status_code == 404

    def test_admin_can_delete_any_project(self, client, admin_token, project):
        resp = client.delete(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 204

    def test_other_user_cannot_delete_returns_403(self, client, other_token, project):
        resp = client.delete(f"/api/v1/projects/{project.id}",
            headers={"Authorization": f"Bearer {other_token}"})
        assert resp.status_code == 403

    def test_delete_without_token_returns_401(self, client, project):
        resp = client.delete(f"/api/v1/projects/{project.id}")
        assert resp.status_code == 401

    def test_delete_nonexistent_returns_404(self, client, user_token):
        resp = client.delete(f"/api/v1/projects/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 404
