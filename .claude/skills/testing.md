# Skill: Testing (TDD)

Todo desarrollo sigue TDD: **test rojo → código mínimo → verde → refactor.**
No se completa ningún endpoint, service ni componente sin sus tests.

---

## Estructura de tests

### Backend

```
backend/
  tests/
    conftest.py              # fixtures globales: db, client, users, tokens
    unit/
      services/
        test_severity_calculator.py
        test_risk_service.py
        test_auth_service.py
        test_audit_service.py
      schemas/
        test_common.py
    integration/
      api/
        test_auth.py
        test_risks.py
        test_issues.py
        test_projects.py
        test_admin.py
```

### Frontend

```
frontend/src/
  __tests__/
    components/
      SeverityBadge.test.jsx
      StatusBadge.test.jsx
      RiskCard.test.jsx
    hooks/
      useRisks.test.js
      useAuth.test.js
    pages/
      Dashboard.test.jsx
```

---

## Backend — patrones

### Unit test de service (DB mockeada)

```python
from unittest.mock import MagicMock, patch
from app.services.risk_service import RiskService

def test_create_risk_calculates_severity():
    db = MagicMock()
    service = RiskService()

    payload = RiskCreate(
        title="Riesgo test",
        probability=ProbabilityLevel.alta,
        impact=ImpactLevel.alto,
        proximity=Proximity.corto_plazo,
        ...
    )
    risk = service.create(db, payload, owner_id=uuid4())

    assert risk.severity == 3          # alta × alto = 0.28 → zona alto → corto_plazo = 3
    assert risk.exposure_zone == "alto"
    db.add.assert_called_once()
    db.commit.assert_called_once()
```

### Unit test puro (sin DB)

```python
# tests/unit/services/test_severity_calculator.py
import pytest
from app.schemas.common import ProbabilityLevel, ImpactLevel, Proximity, ExposureZone
from app.services.severity_calculator import get_exposure, get_exposure_zone, get_severity

@pytest.mark.parametrize("prob,impact,expected", [
    (ProbabilityLevel.muy_alta, ImpactLevel.muy_alto, 0.72),
    (ProbabilityLevel.media,    ImpactLevel.medio,    0.10),
    (ProbabilityLevel.baja,     ImpactLevel.bajo,     0.03),
])
def test_get_exposure(prob, impact, expected):
    assert get_exposure(prob, impact) == expected
```

### Integration test de router (TestClient + DB real de test)

```python
# tests/integration/api/test_risks.py
def test_create_risk_returns_201(client, auth_headers, project):
    response = client.post(
        "/api/v1/risks",
        json={"title": "Test risk", "project_id": str(project.id), ...},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "severity" in data
    assert 1 <= data["severity"] <= 9

def test_create_risk_unauthorized(client):
    response = client.post("/api/v1/risks", json={...})
    assert response.status_code == 401
```

### Fixtures en conftest.py

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db

@pytest.fixture
def db():
    # Usa una DB de test separada
    ...

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db): ...
@pytest.fixture
def regular_user(db): ...
@pytest.fixture
def auth_headers(client, regular_user): ...
@pytest.fixture
def admin_headers(client, admin_user): ...
@pytest.fixture
def project(db, regular_user): ...
```

---

## Frontend — patrones

### Test de componente

```jsx
// src/__tests__/components/SeverityBadge.test.jsx
import { render, screen } from '@testing-library/react'
import SeverityBadge from '../../components/SeverityBadge'

describe('SeverityBadge', () => {
  it('muestra rojo para severidad 1-3', () => {
    render(<SeverityBadge severity={1} />)
    expect(screen.getByTestId('severity-badge')).toHaveClass('severity-red')
  })

  it('muestra amarillo para severidad 4-6', () => {
    render(<SeverityBadge severity={4} />)
    expect(screen.getByTestId('severity-badge')).toHaveClass('severity-yellow')
  })

  it('muestra verde para severidad 7-9', () => {
    render(<SeverityBadge severity={9} />)
    expect(screen.getByTestId('severity-badge')).toHaveClass('severity-green')
  })
})
```

### Test de hook con MSW

```js
// src/__tests__/hooks/useRisks.test.js
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import { useRisks } from '../../hooks/useRisks'

it('carga risks de la API', async () => {
  server.use(
    http.get('/api/v1/risks', () =>
      HttpResponse.json({ items: [{ id: '1', title: 'Test' }], total: 1, page: 1, size: 20, pages: 1 })
    )
  )
  const { result } = renderHook(() => useRisks('project-id'))
  await waitFor(() => expect(result.current.loading).toBe(false))
  expect(result.current.data.items).toHaveLength(1)
})
```

---

## Comandos de test

```bash
# Backend — todos los tests
cd backend && pytest

# Backend — con coverage
cd backend && pytest --cov=app --cov-report=term-missing

# Backend — solo unit tests
cd backend && pytest tests/unit/

# Frontend — todos los tests
cd frontend && npm run test

# Frontend — con coverage
cd frontend && npm run test:coverage
```

---

## Reglas TDD en este proyecto

1. **Test primero**: escribir el test que describe el comportamiento esperado antes del código
2. **Un test a la vez**: rojo → verde → refactor, no escribir todos los tests juntos
3. **Tests independientes**: cada test es autónomo, no depende del orden de ejecución
4. **Nombres descriptivos**: `test_create_risk_calculates_severity_automatically` no `test_create`
5. **Sin lógica en tests**: los tests son declarativos — si hay un `if` en un test, algo está mal
6. **Coverage mínimo**: 80% en services; componentes clave (SeverityBadge, StatusBadge) al 100%
