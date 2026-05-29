import pytest
from app.models.user import User
from app.schemas.common import UserRole, UserStatus
from app.services.auth_service import hash_password, create_access_token


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@example.com",
        full_name="Admin User",
        password_hash=hash_password("adminpass123"),
        role=UserRole.admin,
        status=UserStatus.active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db):
    user = User(
        email="regular@example.com",
        full_name="Regular User",
        password_hash=hash_password("userpass123"),
        role=UserRole.user,
        status=UserStatus.active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def pending_user(db):
    user = User(
        email="pending@example.com",
        full_name="Pending User",
        password_hash=hash_password("pendingpass123"),
        role=UserRole.user,
        status=UserStatus.pending,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(admin_user)


@pytest.fixture
def user_token(regular_user):
    return create_access_token(regular_user)


# ---------------------------------------------------------------------------
# PATCH /admin/users/{id}/approve
# ---------------------------------------------------------------------------

class TestApproveUser:
    def test_admin_can_approve_pending_user(self, client, admin_token, pending_user):
        resp = client.patch(
            f"/api/v1/admin/users/{pending_user.id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "active"

    def test_non_admin_approve_returns_403(self, client, user_token, pending_user):
        resp = client.patch(
            f"/api/v1/admin/users/{pending_user.id}/approve",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    def test_approve_without_token_returns_401(self, client, pending_user):
        resp = client.patch(f"/api/v1/admin/users/{pending_user.id}/approve")
        assert resp.status_code == 401

    def test_approve_nonexistent_user_returns_404(self, client, admin_token):
        import uuid
        fake_id = uuid.uuid4()
        resp = client.patch(
            f"/api/v1/admin/users/{fake_id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /admin/users/{id}/deactivate
# ---------------------------------------------------------------------------

class TestDeactivateUser:
    def test_admin_can_deactivate_active_user(self, client, admin_token, regular_user):
        resp = client.patch(
            f"/api/v1/admin/users/{regular_user.id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "inactive"

    def test_non_admin_deactivate_returns_403(self, client, user_token, pending_user):
        resp = client.patch(
            f"/api/v1/admin/users/{pending_user.id}/deactivate",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    def test_deactivate_nonexistent_user_returns_404(self, client, admin_token):
        import uuid
        fake_id = uuid.uuid4()
        resp = client.patch(
            f"/api/v1/admin/users/{fake_id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /admin/users
# ---------------------------------------------------------------------------

class TestListUsers:
    def test_admin_can_list_users(self, client, admin_token, admin_user, pending_user):
        resp = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert body["total"] >= 2

    def test_non_admin_list_returns_403(self, client, user_token):
        resp = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    def test_list_returns_pagination_fields(self, client, admin_token):
        resp = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        body = resp.json()
        assert all(k in body for k in ["items", "total", "page", "size", "pages"])

    def test_list_page_size_params(self, client, admin_token, admin_user, pending_user, regular_user):
        resp = client.get(
            "/api/v1/admin/users?page=1&size=2",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        body = resp.json()
        assert len(body["items"]) <= 2
        assert body["size"] == 2


# ---------------------------------------------------------------------------
# Audit log recorded on admin user status changes
# ---------------------------------------------------------------------------

class TestAdminActionsAudited:
    def test_approve_user_creates_audit_entry(self, client, admin_token, pending_user):
        import uuid as _uuid
        client.patch(
            f"/api/v1/admin/users/{pending_user.id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        resp = client.get(
            "/api/v1/admin/audit-log?action=approve_user&entity_type=user",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.json()["total"] >= 1
        entry = resp.json()["items"][0]
        assert entry["action"] == "approve_user"
        assert entry["entity_id"] == str(pending_user.id)

    def test_deactivate_user_creates_audit_entry(self, client, admin_token, regular_user):
        client.patch(
            f"/api/v1/admin/users/{regular_user.id}/deactivate",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        resp = client.get(
            "/api/v1/admin/audit-log?action=deactivate_user&entity_type=user",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.json()["total"] >= 1
        entry = resp.json()["items"][0]
        assert entry["action"] == "deactivate_user"
        assert entry["entity_id"] == str(regular_user.id)
