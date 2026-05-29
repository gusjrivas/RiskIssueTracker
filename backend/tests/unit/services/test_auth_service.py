import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.schemas.common import UserRole, UserStatus


# ---------------------------------------------------------------------------
# Helpers — lazy imports so tests fail at collection if module is missing
# ---------------------------------------------------------------------------

def _svc():
    from app.services import auth_service
    return auth_service


def _make_user(status=UserStatus.active, role=UserRole.user, password_hash=None):
    from app.models.user import User
    u = User()
    u.id = uuid.uuid4()
    u.email = "test@example.com"
    u.full_name = "Test User"
    u.role = role
    u.status = status
    u.password_hash = password_hash or _svc().hash_password("password123")
    u.google_id = None
    return u


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = _svc().hash_password("mypassword")
        assert hashed != "mypassword"

    def test_verify_correct_password(self):
        hashed = _svc().hash_password("mypassword")
        assert _svc().verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = _svc().hash_password("mypassword")
        assert _svc().verify_password("wrong", hashed) is False


# ---------------------------------------------------------------------------
# JWT — create / decode
# ---------------------------------------------------------------------------

class TestCreateAccessToken:
    def test_returns_string(self):
        user = _make_user()
        token = _svc().create_access_token(user)
        assert isinstance(token, str)
        assert len(token) > 20

    def test_payload_contains_sub_and_role(self):
        user = _make_user(role=UserRole.admin)
        token = _svc().create_access_token(user)
        payload = _svc().decode_token(token)
        assert payload["sub"] == str(user.id)
        assert payload["role"] == UserRole.admin.value

    def test_different_users_produce_different_tokens(self):
        u1 = _make_user()
        u2 = _make_user()
        u2.id = uuid.uuid4()
        u2.email = "other@example.com"
        assert _svc().create_access_token(u1) != _svc().create_access_token(u2)


class TestDecodeToken:
    def test_valid_token_returns_payload(self):
        user = _make_user()
        token = _svc().create_access_token(user)
        payload = _svc().decode_token(token)
        assert payload["sub"] == str(user.id)

    def test_invalid_token_raises_401(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            _svc().decode_token("not.a.valid.token")
        assert exc.value.status_code == 401

    def test_tampered_token_raises_401(self):
        from fastapi import HTTPException
        user = _make_user()
        token = _svc().create_access_token(user)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException):
            _svc().decode_token(tampered)


# ---------------------------------------------------------------------------
# Register with password
# ---------------------------------------------------------------------------

class TestRegisterWithPassword:
    def _db_no_existing_user(self):
        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = None
        return db

    def _db_existing_user(self):
        from app.models.user import User
        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = User()
        return db

    def test_creates_user_with_pending_status(self):
        db = self._db_no_existing_user()
        db.refresh = MagicMock(side_effect=lambda u: u)
        user = _svc().register_with_password(db, "new@example.com", "password123", "New User")
        assert user.status == UserStatus.pending

    def test_hashes_password(self):
        db = self._db_no_existing_user()
        db.refresh = MagicMock(side_effect=lambda u: u)
        user = _svc().register_with_password(db, "new@example.com", "password123", "New User")
        assert user.password_hash != "password123"
        assert _svc().verify_password("password123", user.password_hash)

    def test_sets_role_to_user(self):
        db = self._db_no_existing_user()
        db.refresh = MagicMock(side_effect=lambda u: u)
        user = _svc().register_with_password(db, "new@example.com", "password123", "New User")
        assert user.role == UserRole.user

    def test_duplicate_email_raises_400(self):
        from fastapi import HTTPException
        db = self._db_existing_user()
        with pytest.raises(HTTPException) as exc:
            _svc().register_with_password(db, "dup@example.com", "password123", "Dup")
        assert exc.value.status_code == 400

    def test_db_add_and_commit_called(self):
        db = self._db_no_existing_user()
        db.refresh = MagicMock(side_effect=lambda u: u)
        _svc().register_with_password(db, "new@example.com", "password123", "New User")
        db.add.assert_called_once()
        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# Authenticate with password
# ---------------------------------------------------------------------------

class TestAuthenticatePassword:
    def test_active_user_correct_password_returns_user(self):
        user = _make_user(status=UserStatus.active)
        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = user
        result = _svc().authenticate_password(db, "test@example.com", "password123")
        assert result is user

    def test_wrong_password_returns_none(self):
        user = _make_user(status=UserStatus.active)
        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = user
        result = _svc().authenticate_password(db, "test@example.com", "wrongpass")
        assert result is None

    def test_nonexistent_email_returns_none(self):
        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = None
        result = _svc().authenticate_password(db, "nobody@example.com", "password123")
        assert result is None

    def test_inactive_user_returns_none(self):
        user = _make_user(status=UserStatus.inactive)
        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = user
        result = _svc().authenticate_password(db, "test@example.com", "password123")
        assert result is None

    def test_pending_user_returns_none(self):
        user = _make_user(status=UserStatus.pending)
        db = MagicMock()
        db.execute.return_value.scalar_one_or_none.return_value = user
        result = _svc().authenticate_password(db, "test@example.com", "password123")
        assert result is None
