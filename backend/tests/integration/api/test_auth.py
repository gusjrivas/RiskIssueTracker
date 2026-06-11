import pytest
from app.models.user import User
from app.schemas.common import UserRole, UserStatus
from app.services.auth_service import hash_password, create_access_token


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

@pytest.fixture
def pending_user(db):
    user = User(
        email="alice@example.com",
        full_name="Alice",
        password_hash=hash_password("password123"),
        role=UserRole.user,
        status=UserStatus.pending,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def active_user(db, pending_user):
    pending_user.status = UserStatus.active
    db.commit()
    db.refresh(pending_user)
    return pending_user


@pytest.fixture
def inactive_user(db):
    user = User(
        email="inactive@example.com",
        full_name="Inactive",
        password_hash=hash_password("password123"),
        role=UserRole.user,
        status=UserStatus.inactive,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def active_token(active_user):
    return create_access_token(active_user)


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_returns_201(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "password": "secure123",
            "full_name": "New User",
        })
        assert resp.status_code == 201

    def test_register_returns_user_response(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "new2@example.com",
            "password": "secure123",
            "full_name": "New User",
        })
        body = resp.json()
        assert body["email"] == "new2@example.com"
        assert body["status"] == "pending"
        assert body["role"] == "user"
        assert "password_hash" not in body

    def test_register_duplicate_email_returns_400(self, client, pending_user):
        resp = client.post("/api/v1/auth/register", json={
            "email": "alice@example.com",
            "password": "secure123",
            "full_name": "Alice Again",
        })
        assert resp.status_code == 400

    def test_register_short_password_returns_422(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "x@example.com",
            "password": "short",
            "full_name": "X",
        })
        assert resp.status_code == 422

    def test_register_missing_email_returns_422(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "password": "secure123",
            "full_name": "No Email",
        })
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_active_user_returns_token(self, client, active_user):
        resp = client.post("/api/v1/auth/login", json={
            "email": "alice@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_pending_user_returns_403(self, client, pending_user):
        resp = client.post("/api/v1/auth/login", json={
            "email": "alice@example.com",
            "password": "password123",
        })
        assert resp.status_code == 403

    def test_login_inactive_user_returns_403(self, client, inactive_user):
        resp = client.post("/api/v1/auth/login", json={
            "email": "inactive@example.com",
            "password": "password123",
        })
        assert resp.status_code == 403

    def test_login_wrong_password_returns_401(self, client, active_user):
        resp = client.post("/api/v1/auth/login", json={
            "email": "alice@example.com",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_login_unknown_email_returns_401(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

class TestMe:
    def test_me_returns_current_user(self, client, active_user, active_token):
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {active_token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "alice@example.com"
        assert body["full_name"] == "Alice"

    def test_me_missing_token_returns_401(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token_returns_401(self, client):
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert resp.status_code == 401

    def test_me_inactive_user_with_valid_token_returns_403(self, client, db, active_user, active_token):
        # El usuario obtuvo el token estando activo y luego fue desactivado:
        # el token vigente no debe seguir dando acceso a la API.
        active_user.status = UserStatus.inactive
        db.commit()
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {active_token}"},
        )
        assert resp.status_code == 403

    def test_me_pending_user_with_valid_token_returns_403(self, client, db, active_user, active_token):
        active_user.status = UserStatus.pending
        db.commit()
        resp = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {active_token}"},
        )
        assert resp.status_code == 403

    def test_inactive_user_cannot_access_protected_endpoints(self, client, db, active_user, active_token):
        active_user.status = UserStatus.inactive
        db.commit()
        resp = client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {active_token}"},
        )
        assert resp.status_code == 403
