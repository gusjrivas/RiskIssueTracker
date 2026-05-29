import uuid
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _svc():
    from app.services import audit_service
    return audit_service


def _db_empty():
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.execute.return_value.scalars.return_value.all.return_value = []
    db.execute.return_value.scalar.return_value = 0
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


# ---------------------------------------------------------------------------
# log_action
# ---------------------------------------------------------------------------

class TestLogAction:
    def test_creates_entry_with_correct_action(self):
        db = _db_empty()
        _svc().log_action(db, user_id=uuid.uuid4(), action="create",
                          entity_type="risk", entity_id=uuid.uuid4())
        db.add.assert_called_once()
        entry = db.add.call_args[0][0]
        assert entry.action == "create"

    def test_creates_entry_with_correct_entity_type(self):
        db = _db_empty()
        entity_id = uuid.uuid4()
        _svc().log_action(db, user_id=uuid.uuid4(), action="update",
                          entity_type="issue", entity_id=entity_id)
        entry = db.add.call_args[0][0]
        assert entry.entity_type == "issue"
        assert uuid.UUID(str(entry.entity_id)) == uuid.UUID(str(entity_id))

    def test_stores_user_id(self):
        db = _db_empty()
        user_id = uuid.uuid4()
        _svc().log_action(db, user_id=user_id, action="delete",
                          entity_type="risk", entity_id=uuid.uuid4())
        entry = db.add.call_args[0][0]
        assert uuid.UUID(str(entry.user_id)) == uuid.UUID(str(user_id))

    def test_stores_changes_when_provided(self):
        db = _db_empty()
        changes = {"from": "open", "to": "in_progress"}
        _svc().log_action(db, user_id=uuid.uuid4(), action="status_change",
                          entity_type="risk", entity_id=uuid.uuid4(), changes=changes)
        entry = db.add.call_args[0][0]
        assert entry.changes == changes

    def test_changes_defaults_to_none(self):
        db = _db_empty()
        _svc().log_action(db, user_id=uuid.uuid4(), action="create",
                          entity_type="project", entity_id=uuid.uuid4())
        entry = db.add.call_args[0][0]
        assert entry.changes is None

    def test_stores_ip_address_when_provided(self):
        db = _db_empty()
        _svc().log_action(db, user_id=uuid.uuid4(), action="login",
                          entity_type="user", entity_id=uuid.uuid4(),
                          ip_address="192.168.1.1")
        entry = db.add.call_args[0][0]
        assert entry.ip_address == "192.168.1.1"

    def test_ip_address_defaults_to_none(self):
        db = _db_empty()
        _svc().log_action(db, user_id=uuid.uuid4(), action="create",
                          entity_type="risk", entity_id=uuid.uuid4())
        entry = db.add.call_args[0][0]
        assert entry.ip_address is None

    def test_calls_commit_after_add(self):
        db = _db_empty()
        _svc().log_action(db, user_id=uuid.uuid4(), action="create",
                          entity_type="risk", entity_id=uuid.uuid4())
        db.commit.assert_called_once()

    def test_user_id_can_be_none(self):
        db = _db_empty()
        _svc().log_action(db, user_id=None, action="create",
                          entity_type="risk", entity_id=uuid.uuid4())
        entry = db.add.call_args[0][0]
        assert entry.user_id is None

    def test_entity_id_can_be_none(self):
        db = _db_empty()
        _svc().log_action(db, user_id=uuid.uuid4(), action="login",
                          entity_type="user", entity_id=None)
        entry = db.add.call_args[0][0]
        assert entry.entity_id is None


# ---------------------------------------------------------------------------
# list_audit_log
# ---------------------------------------------------------------------------

class TestListAuditLog:
    def test_returns_paginated_response(self):
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 3
        db.execute.return_value.scalars.return_value.all.return_value = []
        result = _svc().list_audit_log(db, page=1, size=20)
        for key in ("items", "total", "page", "size", "pages"):
            assert hasattr(result, key)

    def test_total_reflects_count(self):
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 7
        db.execute.return_value.scalars.return_value.all.return_value = []
        result = _svc().list_audit_log(db, page=1, size=20)
        assert result.total == 7
