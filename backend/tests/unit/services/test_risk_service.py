import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.schemas.common import (
    ImpactLevel,
    ProbabilityLevel,
    Proximity,
    RiskCategory,
    RiskStatus,
    UserRole,
    UserStatus,
)
from app.services.severity_calculator import get_severity


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _svc():
    from app.services import risk_service
    return risk_service


def _make_user(role=UserRole.user, user_id=None):
    from app.models.user import User
    u = User()
    u.id = user_id or uuid.uuid4()
    u.email = "user@example.com"
    u.full_name = "Test User"
    u.role = role
    u.status = UserStatus.active
    u.password_hash = "hashed"
    u.google_id = None
    return u


def _make_risk(creator_id=None, owner_id=None, status=RiskStatus.open,
               probability=ProbabilityLevel.media, impact=ImpactLevel.medio,
               proximity=Proximity.mediano_plazo):
    from app.models.risk import Risk
    r = Risk()
    r.id = uuid.uuid4()
    r.project_id = uuid.uuid4()
    r.title = "Test Risk"
    r.description = "A test risk"
    r.category = RiskCategory.costos
    r.probability = probability
    r.impact = impact
    r.proximity = proximity
    r.severity = get_severity(probability, impact, proximity)
    r.status = status
    r.mitigation_strategy = None
    r.contingency_plan = None
    r.owner_id = owner_id
    r.created_by = creator_id or uuid.uuid4()
    r.created_at = datetime.now(timezone.utc)
    r.updated_at = datetime.now(timezone.utc)
    return r


def _db_with(result):
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = result
    db.execute.return_value.scalars.return_value.all.return_value = [result] if result else []
    db.execute.return_value.scalar.return_value = 1 if result else 0
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


def _db_empty():
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    db.execute.return_value.scalars.return_value.all.return_value = []
    db.execute.return_value.scalar.return_value = 0
    db.refresh = MagicMock(side_effect=lambda obj: obj)
    return db


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class TestCreateRisk:
    def test_create_returns_risk_with_correct_fields(self):
        from app.schemas.risk import RiskCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)
        data = RiskCreate(
            project_id=uuid.uuid4(),
            title="New Risk",
            category=RiskCategory.calendario,
            probability=ProbabilityLevel.media,
            impact=ImpactLevel.medio,
            proximity=Proximity.corto_plazo,
        )
        risk = _svc().create_risk(db, data, user)
        assert risk.title == "New Risk"
        assert risk.category == RiskCategory.calendario

    def test_create_sets_created_by_from_current_user(self):
        from app.schemas.risk import RiskCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)
        data = RiskCreate(
            project_id=uuid.uuid4(), title="R",
            category=RiskCategory.costos,
            probability=ProbabilityLevel.baja, impact=ImpactLevel.bajo,
            proximity=Proximity.largo_plazo,
        )
        risk = _svc().create_risk(db, data, user)
        assert uuid.UUID(str(risk.created_by)) == uuid.UUID(str(user.id))

    def test_create_calculates_severity_automatically(self):
        from app.schemas.risk import RiskCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)
        prob, imp, prox = ProbabilityLevel.alta, ImpactLevel.alto, Proximity.corto_plazo
        data = RiskCreate(
            project_id=uuid.uuid4(), title="R",
            category=RiskCategory.equipo,
            probability=prob, impact=imp, proximity=prox,
        )
        risk = _svc().create_risk(db, data, user)
        assert risk.severity == get_severity(prob, imp, prox)

    def test_create_default_status_is_open(self):
        from app.schemas.risk import RiskCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)
        data = RiskCreate(
            project_id=uuid.uuid4(), title="R",
            category=RiskCategory.gestion,
            probability=ProbabilityLevel.baja, impact=ImpactLevel.bajo,
            proximity=Proximity.largo_plazo,
        )
        risk = _svc().create_risk(db, data, user)
        assert risk.status == RiskStatus.open

    def test_create_calls_db_add_and_commit(self):
        from app.schemas.risk import RiskCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)
        data = RiskCreate(
            project_id=uuid.uuid4(), title="R",
            category=RiskCategory.costos,
            probability=ProbabilityLevel.media, impact=ImpactLevel.medio,
            proximity=Proximity.mediano_plazo,
        )
        _svc().create_risk(db, data, user)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_create_with_optional_fields_null(self):
        from app.schemas.risk import RiskCreate
        user = _make_user()
        db = _db_empty()
        db.refresh = MagicMock(side_effect=lambda obj: obj)
        data = RiskCreate(
            project_id=uuid.uuid4(), title="R",
            category=RiskCategory.alcance,
            probability=ProbabilityLevel.baja, impact=ImpactLevel.bajo,
            proximity=Proximity.largo_plazo,
        )
        risk = _svc().create_risk(db, data, user)
        assert risk.mitigation_strategy is None
        assert risk.owner_id is None


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------

class TestGetRisk:
    def test_get_existing_returns_risk(self):
        risk = _make_risk()
        db = _db_with(risk)
        result = _svc().get_risk(db, risk.id)
        assert result is risk

    def test_get_nonexistent_raises_404(self):
        from fastapi import HTTPException
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().get_risk(db, uuid.uuid4())
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class TestUpdateRisk:
    def test_creator_can_update_own_risk(self):
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        risk = _make_risk(creator_id=user.id)
        db = _db_with(risk)
        result = _svc().update_risk(db, risk.id, RiskUpdate(title="New Title"), user)
        assert result.title == "New Title"

    def test_admin_can_update_any_risk(self):
        from app.schemas.risk import RiskUpdate
        admin = _make_user(role=UserRole.admin)
        risk = _make_risk(creator_id=uuid.uuid4())
        db = _db_with(risk)
        result = _svc().update_risk(db, risk.id, RiskUpdate(title="Admin Edit"), admin)
        assert result.title == "Admin Edit"

    def test_other_user_cannot_update_raises_403(self):
        from fastapi import HTTPException
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        risk = _make_risk(creator_id=uuid.uuid4())
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().update_risk(db, risk.id, RiskUpdate(title="Hack"), user)
        assert exc.value.status_code == 403

    def test_update_nonexistent_raises_404(self):
        from fastapi import HTTPException
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().update_risk(db, uuid.uuid4(), RiskUpdate(title="X"), user)
        assert exc.value.status_code == 404

    def test_partial_update_leaves_other_fields_unchanged(self):
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        risk = _make_risk(creator_id=user.id)
        risk.description = "Original"
        db = _db_with(risk)
        _svc().update_risk(db, risk.id, RiskUpdate(title="New Title"), user)
        assert risk.description == "Original"

    def test_update_probability_recalculates_severity(self):
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        risk = _make_risk(creator_id=user.id,
                          probability=ProbabilityLevel.baja,
                          impact=ImpactLevel.bajo,
                          proximity=Proximity.largo_plazo)
        db = _db_with(risk)
        _svc().update_risk(db, risk.id, RiskUpdate(probability=ProbabilityLevel.muy_alta), user)
        expected = get_severity(ProbabilityLevel.muy_alta, ImpactLevel.bajo, Proximity.largo_plazo)
        assert risk.severity == expected

    def test_update_impact_recalculates_severity(self):
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        risk = _make_risk(creator_id=user.id,
                          probability=ProbabilityLevel.media,
                          impact=ImpactLevel.bajo,
                          proximity=Proximity.corto_plazo)
        db = _db_with(risk)
        _svc().update_risk(db, risk.id, RiskUpdate(impact=ImpactLevel.muy_alto), user)
        expected = get_severity(ProbabilityLevel.media, ImpactLevel.muy_alto, Proximity.corto_plazo)
        assert risk.severity == expected

    def test_update_proximity_recalculates_severity(self):
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        risk = _make_risk(creator_id=user.id,
                          probability=ProbabilityLevel.alta,
                          impact=ImpactLevel.alto,
                          proximity=Proximity.largo_plazo)
        db = _db_with(risk)
        _svc().update_risk(db, risk.id, RiskUpdate(proximity=Proximity.corto_plazo), user)
        expected = get_severity(ProbabilityLevel.alta, ImpactLevel.alto, Proximity.corto_plazo)
        assert risk.severity == expected

    def test_update_title_does_not_change_severity(self):
        from app.schemas.risk import RiskUpdate
        user = _make_user()
        risk = _make_risk(creator_id=user.id)
        original_severity = risk.severity
        db = _db_with(risk)
        _svc().update_risk(db, risk.id, RiskUpdate(title="New Title"), user)
        assert risk.severity == original_severity


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestDeleteRisk:
    def test_creator_can_delete_own_risk(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id)
        db = _db_with(risk)
        _svc().delete_risk(db, risk.id, user)
        db.delete.assert_called_once_with(risk)
        db.commit.assert_called_once()

    def test_admin_can_delete_any_risk(self):
        admin = _make_user(role=UserRole.admin)
        risk = _make_risk(creator_id=uuid.uuid4())
        db = _db_with(risk)
        _svc().delete_risk(db, risk.id, admin)
        db.delete.assert_called_once_with(risk)

    def test_other_user_cannot_delete_raises_403(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=uuid.uuid4())
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().delete_risk(db, risk.id, user)
        assert exc.value.status_code == 403

    def test_delete_nonexistent_raises_404(self):
        from fastapi import HTTPException
        user = _make_user()
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().delete_risk(db, uuid.uuid4(), user)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

class TestTransitionStatus:
    def test_creator_can_transition(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.open)
        db = _db_with(risk)
        result = _svc().transition_status(db, risk.id, RiskStatus.in_progress, user)
        assert result.status == RiskStatus.in_progress

    def test_owner_can_transition(self):
        owner = _make_user()
        risk = _make_risk(owner_id=owner.id, status=RiskStatus.open)
        db = _db_with(risk)
        result = _svc().transition_status(db, risk.id, RiskStatus.in_progress, owner)
        assert result.status == RiskStatus.in_progress

    def test_admin_can_transition_any_risk(self):
        admin = _make_user(role=UserRole.admin)
        risk = _make_risk(creator_id=uuid.uuid4(), status=RiskStatus.open)
        db = _db_with(risk)
        result = _svc().transition_status(db, risk.id, RiskStatus.in_progress, admin)
        assert result.status == RiskStatus.in_progress

    def test_other_user_cannot_transition_raises_403(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=uuid.uuid4(), owner_id=uuid.uuid4(), status=RiskStatus.open)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, risk.id, RiskStatus.in_progress, user)
        assert exc.value.status_code == 403

    def test_open_to_in_progress_valid(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.open)
        db = _db_with(risk)
        result = _svc().transition_status(db, risk.id, RiskStatus.in_progress, user)
        assert result.status == RiskStatus.in_progress

    def test_in_progress_to_closed_valid(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        result = _svc().transition_status(db, risk.id, RiskStatus.closed, user)
        assert result.status == RiskStatus.closed

    def test_in_progress_to_derived_valid(self):
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.in_progress)
        db = _db_with(risk)
        result = _svc().transition_status(db, risk.id, RiskStatus.derived, user)
        assert result.status == RiskStatus.derived

    def test_open_to_closed_invalid_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.open)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, risk.id, RiskStatus.closed, user)
        assert exc.value.status_code == 409

    def test_open_to_derived_invalid_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.open)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, risk.id, RiskStatus.derived, user)
        assert exc.value.status_code == 409

    def test_closed_to_in_progress_invalid_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.closed)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, risk.id, RiskStatus.in_progress, user)
        assert exc.value.status_code == 409

    def test_derived_is_terminal_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.derived)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, risk.id, RiskStatus.closed, user)
        assert exc.value.status_code == 409

    def test_same_status_raises_409(self):
        from fastapi import HTTPException
        user = _make_user()
        risk = _make_risk(creator_id=user.id, status=RiskStatus.open)
        db = _db_with(risk)
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, risk.id, RiskStatus.open, user)
        assert exc.value.status_code == 409

    def test_transition_nonexistent_raises_404(self):
        from fastapi import HTTPException
        user = _make_user()
        db = _db_empty()
        with pytest.raises(HTTPException) as exc:
            _svc().transition_status(db, uuid.uuid4(), RiskStatus.in_progress, user)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------

class TestListRisks:
    def test_list_returns_paginated_response(self):
        risk = _make_risk()
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 1
        db.execute.return_value.scalars.return_value.all.return_value = [risk]
        result = _svc().list_risks(db, page=1, size=20)
        for key in ("items", "total", "page", "size", "pages"):
            assert hasattr(result, key)

    def test_list_total_reflects_db_count(self):
        db = MagicMock()
        db.execute.return_value.scalar.return_value = 5
        db.execute.return_value.scalars.return_value.all.return_value = []
        result = _svc().list_risks(db, page=1, size=20)
        assert result.total == 5
