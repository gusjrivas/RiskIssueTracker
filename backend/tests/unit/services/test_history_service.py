import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.schemas.common import EntityType, IssueStatus, RiskStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _svc():
    from app.services import history_service
    return history_service


def _make_entry(entity_type=EntityType.risk, entity_id=None,
                from_status="open", to_status="in_progress", changed_by=None):
    from app.models.history_entry import HistoryEntry
    e = HistoryEntry()
    e.id = uuid.uuid4()
    e.entity_type = entity_type
    e.entity_id = entity_id or uuid.uuid4()
    e.from_status = from_status
    e.to_status = to_status
    e.changed_by = changed_by or uuid.uuid4()
    e.notes = None
    e.created_at = datetime.now(timezone.utc)
    return e


def _db_empty():
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.execute.return_value.scalars.return_value.all.return_value = []
    db.execute.return_value.scalar.return_value = 0
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


def _db_with(result):
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = result
    db.execute.return_value.scalars.return_value.all.return_value = [result] if result else []
    db.execute.return_value.scalar.return_value = 1 if result else 0
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


# ---------------------------------------------------------------------------
# record_transition
# ---------------------------------------------------------------------------

class TestRecordTransition:
    def test_creates_history_entry_with_correct_fields(self):
        db = _db_empty()
        entity_id = uuid.uuid4()
        changed_by = uuid.uuid4()
        _svc().record_transition(
            db,
            entity_type=EntityType.risk,
            entity_id=entity_id,
            from_status=RiskStatus.open,
            to_status=RiskStatus.in_progress,
            changed_by_id=changed_by,
        )
        db.add.assert_called_once()
        entry = db.add.call_args[0][0]
        assert entry.entity_type == EntityType.risk
        assert uuid.UUID(str(entry.entity_id)) == uuid.UUID(str(entity_id))
        assert entry.from_status == RiskStatus.open.value
        assert entry.to_status == RiskStatus.in_progress.value
        assert uuid.UUID(str(entry.changed_by)) == uuid.UUID(str(changed_by))

    def test_records_issue_transition(self):
        db = _db_empty()
        entity_id = uuid.uuid4()
        _svc().record_transition(
            db,
            entity_type=EntityType.issue,
            entity_id=entity_id,
            from_status=IssueStatus.open,
            to_status=IssueStatus.in_progress,
            changed_by_id=uuid.uuid4(),
        )
        db.add.assert_called_once()
        entry = db.add.call_args[0][0]
        assert entry.entity_type == EntityType.issue

    def test_from_status_can_be_none(self):
        db = _db_empty()
        _svc().record_transition(
            db,
            entity_type=EntityType.risk,
            entity_id=uuid.uuid4(),
            from_status=None,
            to_status=RiskStatus.open,
            changed_by_id=uuid.uuid4(),
        )
        entry = db.add.call_args[0][0]
        assert entry.from_status is None

    def test_notes_are_stored_when_provided(self):
        db = _db_empty()
        _svc().record_transition(
            db,
            entity_type=EntityType.risk,
            entity_id=uuid.uuid4(),
            from_status=RiskStatus.open,
            to_status=RiskStatus.in_progress,
            changed_by_id=uuid.uuid4(),
            notes="Urgent escalation",
        )
        entry = db.add.call_args[0][0]
        assert entry.notes == "Urgent escalation"

    def test_calls_commit_after_add(self):
        db = _db_empty()
        _svc().record_transition(
            db,
            entity_type=EntityType.risk,
            entity_id=uuid.uuid4(),
            from_status=RiskStatus.open,
            to_status=RiskStatus.in_progress,
            changed_by_id=uuid.uuid4(),
        )
        db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# list_history
# ---------------------------------------------------------------------------

class TestListHistory:
    def test_list_returns_paginated_response(self):
        entry = _make_entry()
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 1
        db.execute.return_value.scalars.return_value.all.return_value = [entry]
        result = _svc().list_history(
            db, entity_type=EntityType.risk, entity_id=entry.entity_id,
            page=1, size=20,
        )
        for key in ("items", "total", "page", "size", "pages"):
            assert hasattr(result, key)

    def test_list_total_reflects_db_count(self):
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 4
        db.execute.return_value.scalars.return_value.all.return_value = []
        result = _svc().list_history(
            db, entity_type=EntityType.risk, entity_id=uuid.uuid4(),
            page=1, size=20,
        )
        assert result.total == 4

    def test_list_filters_by_entity_type_and_id(self):
        entry = _make_entry()
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 1
        db.execute.return_value.scalars.return_value.all.return_value = [entry]
        result = _svc().list_history(
            db, entity_type=entry.entity_type, entity_id=entry.entity_id,
            page=1, size=20,
        )
        assert result.total == 1
