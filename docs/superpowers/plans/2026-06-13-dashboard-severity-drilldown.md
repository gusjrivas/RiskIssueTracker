# Dashboard Severity Drill-down (Flip Cards) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cada celda de la matriz de severidad del dashboard (`/dashboard`) se voltea al hacer click y muestra un listado de links a los riesgos/issues con esa severidad (título + estado), respetando la visibilidad por usuario, y navega al detalle al hacer click en un link.

**Architecture:** Nuevo endpoint backend `GET /api/v1/dashboard/stats/severity/{severity}?type=risk|issue` que reutiliza el filtro de visibilidad existente en `dashboard_service.py`. En el frontend, un nuevo componente `SeverityCellFlip` (flip 3D con framer-motion) reemplaza el contenido de cada celda de `SeverityMatrixGrid`, con un hook `useSeverityItems` que hace fetch on-demand y cachea por `severity-type`.

**Tech Stack:** FastAPI, SQLAlchemy 2.0, Pydantic v2, pytest (backend) · React, framer-motion, react-router-dom, Vitest + Testing Library (frontend)

---

## Task 1: Backend — endpoint `GET /dashboard/stats/severity/{severity}`

**Files:**
- Modify: `backend/app/schemas/dashboard.py`
- Modify: `backend/app/services/dashboard_service.py`
- Modify: `backend/app/api/dashboard.py`
- Test: `backend/tests/integration/api/test_dashboard.py`

- [ ] **Step 1: Write the failing tests**

Append to the end of `backend/tests/integration/api/test_dashboard.py` (after the existing `TestDashboardStats` class):

```python
def _get_severity_items(client, token, severity, type_):
    return client.get(
        f"/api/v1/dashboard/stats/severity/{severity}?type={type_}",
        headers={"Authorization": f"Bearer {token}"},
    )


# ---------------------------------------------------------------------------
# GET /dashboard/stats/severity/{severity}
# ---------------------------------------------------------------------------

class TestSeverityItems:
    def test_requires_auth(self, client):
        resp = client.get("/api/v1/dashboard/stats/severity/1?type=risk")
        assert resp.status_code in (401, 403)

    def test_admin_sees_all_risks_for_severity(self, client, admin_token, seed):
        resp = _get_severity_items(client, admin_token, 1, "risk")
        assert resp.status_code == 200
        items = resp.json()["items"]
        # risk_a1 (open) + risk_a3 (open, owner=regular_user) — ambos severidad 1
        assert len(items) == 2
        assert {i["title"] for i in items} == {"Risk sev 1"}
        assert {i["status"] for i in items} == {"open"}

    def test_admin_sees_issue_for_severity(self, client, admin_token, seed):
        resp = _get_severity_items(client, admin_token, 9, "issue")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["title"] == "Issue sev 9"
        assert items[0]["status"] == "closed"

    def test_regular_user_sees_only_visible_risks(self, client, user_token, seed):
        # severidad 1: solo ve risk_a3 (es owner), no risk_a1 (de admin)
        resp = _get_severity_items(client, user_token, 1, "risk")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

        # severidad 4: ve risk_b1 porque project_b es propio (created_by)
        resp_b = _get_severity_items(client, user_token, 4, "risk")
        items_b = resp_b.json()["items"]
        assert len(items_b) == 1
        assert items_b[0]["status"] == "derived"

    def test_regular_user_does_not_see_others_issues(self, client, user_token, seed):
        # severidad 9 (issue_a1) pertenece al admin en project_a -> no visible
        resp = _get_severity_items(client, user_token, 9, "issue")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_severity_out_of_range_returns_422(self, client, admin_token):
        assert _get_severity_items(client, admin_token, 0, "risk").status_code == 422
        assert _get_severity_items(client, admin_token, 10, "risk").status_code == 422

    def test_invalid_type_returns_422(self, client, admin_token):
        resp = _get_severity_items(client, admin_token, 1, "foo")
        assert resp.status_code == 422

    def test_severity_without_items_returns_empty_list(self, client, admin_token, seed):
        resp = _get_severity_items(client, admin_token, 7, "risk")
        assert resp.status_code == 200
        assert resp.json()["items"] == []

    def test_deleted_risk_excluded(self, client, admin_token, seed):
        # risk_a4 (severidad 2) tiene deleted_at seteado en el seed
        resp = _get_severity_items(client, admin_token, 2, "risk")
        assert resp.status_code == 200
        assert resp.json()["items"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && pytest tests/integration/api/test_dashboard.py::TestSeverityItems -v`
Expected: FAIL with 404 (route `/dashboard/stats/severity/{severity}` does not exist)

- [ ] **Step 3: Add response schemas**

In `backend/app/schemas/dashboard.py`, add `uuid` import and the two new classes (keep the existing `EntityStats`/`DashboardStatsResponse`):

```python
import uuid

from pydantic import BaseModel


class EntityStats(BaseModel):
    total: int
    # Claves de severidad "1".."9" como string (JSON no admite claves int),
    # siempre zero-filled para que el frontend no necesite defaults.
    by_severity: dict[str, int]
    by_status: dict[str, int]


class DashboardStatsResponse(BaseModel):
    risks: EntityStats
    issues: EntityStats


class SeverityItem(BaseModel):
    id: uuid.UUID
    title: str
    status: str


class SeverityItemsResponse(BaseModel):
    items: list[SeverityItem]
```

- [ ] **Step 4: Add service function**

In `backend/app/services/dashboard_service.py`, update the imports at the top and add `get_severity_items` at the end of the file:

```python
from enum import Enum
from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.issue import Issue
from app.models.project import Project
from app.models.risk import Risk
from app.models.user import User
from app.schemas.common import IssueStatus, RiskStatus, UserRole
from app.schemas.dashboard import (
    DashboardStatsResponse,
    EntityStats,
    SeverityItem,
    SeverityItemsResponse,
)
```

Add at the end of the file:

```python
def get_severity_items(
    db: Session,
    severity: int,
    entity_type: Literal["risk", "issue"],
    current_user: User,
) -> SeverityItemsResponse:
    model = Risk if entity_type == "risk" else Issue
    conditions = [model.deleted_at.is_(None), model.severity == severity]

    visibility = _visibility_clause(model, current_user)
    if visibility is not None:
        conditions.append(visibility)

    rows = db.execute(
        select(model.id, model.title, model.status).where(*conditions)
    ).all()

    return SeverityItemsResponse(
        items=[
            SeverityItem(id=row.id, title=row.title, status=row.status.value)
            for row in rows
        ]
    )
```

- [ ] **Step 5: Add router endpoint**

Replace the full contents of `backend/app/api/dashboard.py`:

```python
from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardStatsResponse, SeverityItemsResponse
from app.services import dashboard_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_stats(db, current_user)


@router.get("/stats/severity/{severity}", response_model=SeverityItemsResponse)
def get_severity_items(
    severity: int = Path(ge=1, le=9),
    type: Literal["risk", "issue"] = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_severity_items(db, severity, type, current_user)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd backend && pytest tests/integration/api/test_dashboard.py -v`
Expected: PASS (all tests in `TestDashboardStats` and `TestSeverityItems`)

- [ ] **Step 7: Run full backend test suite**

Run: `cd backend && pytest`
Expected: PASS, no regressions

- [ ] **Step 8: Commit**

```bash
git add backend/app/schemas/dashboard.py backend/app/services/dashboard_service.py backend/app/api/dashboard.py backend/tests/integration/api/test_dashboard.py
git commit -m "feat: endpoint de drill-down por severidad en el dashboard (backend)"
```

---

## Task 2: Frontend — `useSeverityItems` hook + API function

**Files:**
- Modify: `frontend/src/api/dashboard.js`
- Create: `frontend/src/hooks/useSeverityItems.js`
- Test: `frontend/src/__tests__/hooks/useSeverityItems.test.jsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/__tests__/hooks/useSeverityItems.test.jsx`:

```jsx
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useSeverityItems } from '../../hooks/useSeverityItems'
import * as dashboardApi from '../../api/dashboard'

vi.mock('../../api/dashboard')

describe('useSeverityItems', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('carga items para severity+type y los expone en itemsByKey', async () => {
    dashboardApi.getSeverityItems.mockResolvedValue({
      items: [{ id: '1', title: 'Risk 1', status: 'open' }],
    })
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(1, 'risk')
    })

    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'risk')
    expect(result.current.itemsByKey['1-risk']).toEqual([
      { id: '1', title: 'Risk 1', status: 'open' },
    ])
    expect(result.current.loadingByKey['1-risk']).toBe(false)
  })

  it('no vuelve a pedir datos para la misma severity+type (cache)', async () => {
    dashboardApi.getSeverityItems.mockResolvedValue({ items: [] })
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(2, 'issue')
    })
    await act(async () => {
      await result.current.fetchItems(2, 'issue')
    })

    expect(dashboardApi.getSeverityItems).toHaveBeenCalledTimes(1)
  })

  it('cachea por separado severity+type distintos', async () => {
    dashboardApi.getSeverityItems.mockResolvedValue({ items: [] })
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(1, 'risk')
    })
    await act(async () => {
      await result.current.fetchItems(1, 'issue')
    })

    expect(dashboardApi.getSeverityItems).toHaveBeenCalledTimes(2)
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'risk')
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'issue')
  })

  it('expone error si la API falla', async () => {
    dashboardApi.getSeverityItems.mockRejectedValue(new Error('boom'))
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(3, 'risk')
    })

    expect(result.current.errorByKey['3-risk']).toBe('boom')
    expect(result.current.loadingByKey['3-risk']).toBe(false)
    expect(result.current.itemsByKey['3-risk']).toBeUndefined()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/__tests__/hooks/useSeverityItems.test.jsx`
Expected: FAIL — `useSeverityItems` and `getSeverityItems` do not exist yet

- [ ] **Step 3: Add API function**

In `frontend/src/api/dashboard.js`, add the new export (keep the existing `getDashboardStats`):

```js
import { apiGet } from './client'

export const getDashboardStats = () => apiGet('/api/v1/dashboard/stats')

export const getSeverityItems = (severity, type) =>
  apiGet(`/api/v1/dashboard/stats/severity/${severity}?type=${type}`)
```

- [ ] **Step 4: Create the hook**

Create `frontend/src/hooks/useSeverityItems.js`:

```js
import { useState, useRef, useCallback } from 'react'
import * as dashboardApi from '../api/dashboard'

// Hook con cache en memoria por clave `severity-type`, para que cada celda de
// la matriz de severidad pueda pedir sus riesgos/issues sin re-fetchear si
// ya se cargaron antes.
export function useSeverityItems() {
  const [itemsByKey, setItemsByKey] = useState({})
  const [loadingByKey, setLoadingByKey] = useState({})
  const [errorByKey, setErrorByKey] = useState({})
  const cache = useRef({})

  const fetchItems = useCallback(async (severity, type) => {
    const key = `${severity}-${type}`
    if (cache.current[key]) return

    setLoadingByKey(prev => ({ ...prev, [key]: true }))
    try {
      const res = await dashboardApi.getSeverityItems(severity, type)
      cache.current[key] = res.items
      setItemsByKey(prev => ({ ...prev, [key]: res.items }))
      setErrorByKey(prev => ({ ...prev, [key]: null }))
    } catch (e) {
      setErrorByKey(prev => ({ ...prev, [key]: e.message }))
    } finally {
      setLoadingByKey(prev => ({ ...prev, [key]: false }))
    }
  }, [])

  return { itemsByKey, loadingByKey, errorByKey, fetchItems }
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/__tests__/hooks/useSeverityItems.test.jsx`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/dashboard.js frontend/src/hooks/useSeverityItems.js frontend/src/__tests__/hooks/useSeverityItems.test.jsx
git commit -m "feat: hook useSeverityItems con fetch on-demand y cache (frontend)"
```

---

## Task 3: Frontend — `SeverityCellFlip` component

**Files:**
- Create: `frontend/src/components/SeverityCellFlip.jsx`
- Test: `frontend/src/__tests__/components/SeverityCellFlip.test.jsx`

- [ ] **Step 1: Write the failing test**

Create `frontend/src/__tests__/components/SeverityCellFlip.test.jsx`:

```jsx
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import SeverityCellFlip from '../../components/SeverityCellFlip'
import * as useSeverityItemsModule from '../../hooks/useSeverityItems'

vi.mock('../../hooks/useSeverityItems')

function setup({ itemsByKey = {}, loadingByKey = {}, errorByKey = {} } = {}, props = {}) {
  const fetchItems = vi.fn()
  useSeverityItemsModule.useSeverityItems.mockReturnValue({
    itemsByKey,
    loadingByKey,
    errorByKey,
    fetchItems,
  })
  render(
    <MemoryRouter>
      <SeverityCellFlip sev={1} risksCount={2} issuesCount={1} {...props} />
    </MemoryRouter>
  )
  return { fetchItems }
}

describe('SeverityCellFlip', () => {
  it('muestra la cara frontal con los conteos y el número de severidad', () => {
    setup()
    const front = screen.getByTestId('matrix-cell-1')
    expect(front).toHaveTextContent('2 riesgos')
    expect(front).toHaveTextContent('1 issue')
    expect(screen.getByTestId('matrix-sev-1')).toHaveTextContent('1')
    expect(screen.queryByTestId('matrix-cell-back-1')).not.toBeInTheDocument()
  })

  it('al hacer click se voltea, muestra la cara trasera y dispara fetchItems para risk e issue', () => {
    const { fetchItems } = setup({ itemsByKey: { '1-risk': [], '1-issue': [] } })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    expect(screen.getByTestId('matrix-cell-back-1')).toBeInTheDocument()
    expect(fetchItems).toHaveBeenCalledWith(1, 'risk')
    expect(fetchItems).toHaveBeenCalledWith(1, 'issue')
  })

  it('renderiza links a riesgos e issues con su StatusBadge', () => {
    setup({
      itemsByKey: {
        '1-risk': [{ id: 'r1', title: 'Riesgo crítico', status: 'open' }],
        '1-issue': [{ id: 'i1', title: 'Issue crítico', status: 'closed' }],
      },
    })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    const riskLink = screen.getByRole('link', { name: /Riesgo crítico/ })
    expect(riskLink).toHaveAttribute('href', '/risks/r1')

    const issueLink = screen.getByRole('link', { name: /Issue crítico/ })
    expect(issueLink).toHaveAttribute('href', '/issues/i1')
  })

  it('muestra mensajes cuando no hay riesgos ni issues para la severidad', () => {
    setup({ itemsByKey: { '1-risk': [], '1-issue': [] } })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    expect(screen.getByText('No hay riesgos con esta severidad.')).toBeInTheDocument()
    expect(screen.getByText('No hay issues con esta severidad.')).toBeInTheDocument()
  })

  it('el botón de cierre vuelve a la cara frontal', () => {
    setup({ itemsByKey: { '1-risk': [], '1-issue': [] } })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))
    expect(screen.getByTestId('matrix-cell-back-1')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('flip-close-1'))
    expect(screen.queryByTestId('matrix-cell-back-1')).not.toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/__tests__/components/SeverityCellFlip.test.jsx`
Expected: FAIL — module `../../components/SeverityCellFlip` does not exist

- [ ] **Step 3: Create the component**

Create `frontend/src/components/SeverityCellFlip.jsx`:

```jsx
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { X } from 'lucide-react'
import { severityClass } from './SeverityBadge'
import StatusBadge from './StatusBadge'
import { useSeverityItems } from '../hooks/useSeverityItems'

function plural(n, singular, pluralForm) {
  return `${n} ${n === 1 ? singular : pluralForm}`
}

function ItemList({ items, loading, emptyLabel, basePath }) {
  if (loading) {
    return <p className="text-[10px] text-muted">Cargando...</p>
  }
  if (!items || items.length === 0) {
    return <p className="text-[10px] text-muted">{emptyLabel}</p>
  }
  return (
    <div className="space-y-1">
      {items.map(item => (
        <Link
          key={item.id}
          to={`${basePath}/${item.id}`}
          className="flex items-center justify-between gap-2 text-[11px] hover:underline"
        >
          <span className="truncate">{item.title}</span>
          <StatusBadge status={item.status} />
        </Link>
      ))}
    </div>
  )
}

// Celda de la matriz de severidad con flip 3D: la cara frontal muestra los
// conteos (igual que antes); al hacer click se voltea y la cara trasera
// lista los riesgos/issues de esa severidad, con link directo al detalle.
export default function SeverityCellFlip({ sev, risksCount, issuesCount }) {
  const [flipped, setFlipped] = useState(false)
  const { itemsByKey, loadingByKey, fetchItems } = useSeverityItems()

  const openBack = () => {
    fetchItems(sev, 'risk')
    fetchItems(sev, 'issue')
    setFlipped(true)
  }

  return (
    <div className="relative" style={{ perspective: '1000px' }}>
      <motion.div
        className="relative w-full"
        style={{ transformStyle: 'preserve-3d' }}
        animate={{ rotateY: flipped ? 180 : 0 }}
        transition={{ duration: 0.4, ease: 'easeInOut' }}
      >
        <button
          type="button"
          onClick={openBack}
          data-testid={`matrix-cell-${sev}`}
          style={{ backfaceVisibility: 'hidden' }}
          className={`${severityClass(sev)} relative flex flex-col items-center justify-center gap-1.5 py-6 px-3 w-full`}
        >
          <span className="font-display text-2xl font-bold leading-none">
            {plural(risksCount, 'riesgo', 'riesgos')}
          </span>
          <span className="font-display text-lg font-semibold leading-none opacity-75">
            {plural(issuesCount, 'issue', 'issues')}
          </span>
          <span
            data-testid={`matrix-sev-${sev}`}
            className="absolute bottom-1.5 left-2 text-[10px] font-medium opacity-50 leading-none"
          >
            {sev}
          </span>
        </button>

        {flipped && (
          <div
            data-testid={`matrix-cell-back-${sev}`}
            style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
            className="absolute inset-0 flex flex-col gap-2 p-2 bg-surface border border-border overflow-hidden"
          >
            <button
              type="button"
              data-testid={`flip-close-${sev}`}
              onClick={() => setFlipped(false)}
              className="self-end text-muted hover:text-ink"
            >
              <X size={12} />
            </button>

            <div className="flex-1 overflow-y-auto max-h-24">
              <p className="text-[10px] font-semibold text-muted mb-1">Riesgos</p>
              <ItemList
                items={itemsByKey[`${sev}-risk`]}
                loading={loadingByKey[`${sev}-risk`]}
                emptyLabel="No hay riesgos con esta severidad."
                basePath="/risks"
              />
            </div>

            <div className="flex-1 overflow-y-auto max-h-24">
              <p className="text-[10px] font-semibold text-muted mb-1">Issues</p>
              <ItemList
                items={itemsByKey[`${sev}-issue`]}
                loading={loadingByKey[`${sev}-issue`]}
                emptyLabel="No hay issues con esta severidad."
                basePath="/issues"
              />
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/__tests__/components/SeverityCellFlip.test.jsx`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/SeverityCellFlip.jsx frontend/src/__tests__/components/SeverityCellFlip.test.jsx
git commit -m "feat: componente SeverityCellFlip con flip 3D y listado de links (frontend)"
```

---

## Task 4: Frontend — integrar `SeverityCellFlip` en `SeverityMatrixGrid`

**Files:**
- Modify: `frontend/src/components/SeverityMatrixGrid.jsx`
- Modify: `frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx`

- [ ] **Step 1: Update the test file**

Replace the full contents of `frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx`:

```jsx
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SeverityMatrixGrid from '../../components/SeverityMatrixGrid'
import * as dashboardApi from '../../api/dashboard'

vi.mock('../../api/dashboard')

const risksBySeverity = { 1: 3, 2: 0, 3: 1, 4: 0, 5: 2, 6: 0, 7: 0, 8: 0, 9: 4 }
const issuesBySeverity = { 1: 1, 2: 0, 3: 0, 4: 5, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0 }

function renderGrid(risks = risksBySeverity, issues = issuesBySeverity) {
  return render(
    <MemoryRouter>
      <SeverityMatrixGrid risksBySeverity={risks} issuesBySeverity={issues} />
    </MemoryRouter>
  )
}

describe('SeverityMatrixGrid', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    dashboardApi.getSeverityItems.mockResolvedValue({ items: [] })
  })

  it('renderiza las 9 celdas de severidad', () => {
    renderGrid()
    for (let s = 1; s <= 9; s++) {
      expect(screen.getByTestId(`matrix-cell-${s}`)).toBeInTheDocument()
    }
  })

  it('colorea cada celda según la zona de severidad', () => {
    renderGrid()
    expect(screen.getByTestId('matrix-cell-2')).toHaveClass('severity-red')
    expect(screen.getByTestId('matrix-cell-5')).toHaveClass('severity-yellow')
    expect(screen.getByTestId('matrix-cell-9')).toHaveClass('severity-green')
  })

  it('muestra el número de severidad como indicador pequeño en la esquina de cada celda', () => {
    renderGrid()
    for (let s = 1; s <= 9; s++) {
      const indicator = screen.getByTestId(`matrix-sev-${s}`)
      expect(indicator).toHaveTextContent(String(s))
      expect(indicator).toHaveClass('absolute', 'bottom-1.5', 'left-2')
    }
  })

  it('muestra los counts de risks e issues dentro de cada celda', () => {
    renderGrid()
    const cell1 = screen.getByTestId('matrix-cell-1')
    expect(cell1).toHaveTextContent('3 riesgos')
    expect(cell1).toHaveTextContent('1 issue')
    const cell4 = screen.getByTestId('matrix-cell-4')
    expect(cell4).toHaveTextContent('0 riesgos')
    expect(cell4).toHaveTextContent('5 issues')
  })

  it('muestra los labels de proximidad y zona en español', () => {
    renderGrid()
    expect(screen.getByText('Corto plazo')).toBeInTheDocument()
    expect(screen.getByText('Mediano plazo')).toBeInTheDocument()
    expect(screen.getByText('Largo plazo')).toBeInTheDocument()
    expect(screen.getByText('Zona Bajo')).toBeInTheDocument()
    expect(screen.getByText('Zona Medio')).toBeInTheDocument()
    expect(screen.getByText('Zona Alto')).toBeInTheDocument()
  })

  it('no rompe si los maps vienen vacíos', () => {
    renderGrid({}, {})
    expect(screen.getByTestId('matrix-cell-1')).toHaveTextContent('0 riesgos')
  })

  it('al hacer click sobre una celda se voltea y pide los riesgos/issues de esa severidad', () => {
    renderGrid()
    fireEvent.click(screen.getByTestId('matrix-cell-1'))
    expect(screen.getByTestId('matrix-cell-back-1')).toBeInTheDocument()
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'risk')
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'issue')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/__tests__/components/SeverityMatrixGrid.test.jsx`
Expected: FAIL — `matrix-cell-back-1` not found (grid still renders plain divs, not `SeverityCellFlip`)

- [ ] **Step 3: Update `SeverityMatrixGrid.jsx`**

Replace the full contents of `frontend/src/components/SeverityMatrixGrid.jsx`:

```jsx
import { SEVERITY_MATRIX, PROXIMITY_LABELS, ZONE_LABELS } from '../utils/severityCalc'
import SeverityCellFlip from './SeverityCellFlip'

const ZONES = ['bajo', 'medio', 'alto']

// Grilla 3×3 de la matriz de severidad (proximidad × zona de exposición).
// Cada celda corresponde a un único valor de severidad 1-9 (la matriz es
// biyectiva). Cada celda es un SeverityCellFlip: muestra conteos y, al
// hacer click, se voltea y lista los riesgos/issues de esa severidad.
export default function SeverityMatrixGrid({ risksBySeverity = {}, issuesBySeverity = {} }) {
  return (
    <div className="grid grid-cols-[auto_1fr_1fr_1fr] gap-2">
      <div />
      {ZONES.map(zone => (
        <div key={zone} className="text-xs font-medium text-muted text-center pb-1">
          Zona {ZONE_LABELS[zone]}
        </div>
      ))}

      {Object.entries(SEVERITY_MATRIX).map(([proximity, row]) => (
        <div key={proximity} className="contents">
          <div className="text-xs font-medium text-muted flex items-center pr-2">
            {PROXIMITY_LABELS[proximity]}
          </div>
          {ZONES.map(zone => {
            const sev = row[zone]
            return (
              <SeverityCellFlip
                key={zone}
                sev={sev}
                risksCount={risksBySeverity[sev] ?? 0}
                issuesCount={issuesBySeverity[sev] ?? 0}
              />
            )
          })}
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/__tests__/components/SeverityMatrixGrid.test.jsx`
Expected: PASS (7 tests)

- [ ] **Step 5: Run full frontend test suite**

Run: `cd frontend && npx vitest run`
Expected: PASS, no regressions (especially `DashboardStatsPage`/`useDashboardStats` tests, unaffected by this change)

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/SeverityMatrixGrid.jsx frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx
git commit -m "feat: integrar SeverityCellFlip en SeverityMatrixGrid"
```

---

## Task 5: Verificación manual end-to-end

**Files:** ninguno (solo verificación manual)

- [ ] **Step 1: Levantar la app**

Run: `docker compose up -d` (o `docker compose up -d --build` si las dependencias cambiaron — no es el caso en este plan)

- [ ] **Step 2: Verificar visualmente en el navegador**

1. Login como admin y como un user regular (en dos sesiones/navegadores si es posible).
2. Ir a `/dashboard`.
3. Click en una celda de la matriz con riesgos/issues > 0 → debe voltearse (animación 3D) y mostrar "Riesgos" e "Issues" con título + `StatusBadge`.
4. Click en un link de riesgo → navega a `/risks/{id}` y muestra el detalle correcto.
5. Click en un link de issue → navega a `/issues/{id}` y muestra el detalle correcto.
6. Click en una celda con 0 riesgos y 0 issues → se voltea y muestra los dos mensajes de "No hay...".
7. Click en el botón de cierre → vuelve a la cara frontal.
8. Voltear dos celdas distintas simultáneamente → ambas permanecen volteadas.
9. Como user regular: confirmar que los listados solo incluyen riesgos/issues propios (owner/creador/proyecto propio), igual que ya ocurre con los conteos de `/dashboard/stats`.

- [ ] **Step 3: Commit final (si hubo ajustes manuales)**

Si la verificación manual no requirió cambios, no hay nada que commitear en este paso.

---

## Self-review checklist (completado durante la escritura del plan)

- **Cobertura del spec**: endpoint backend (Task 1), API + hook con cache (Task 2), componente flip con 2 secciones y mensajes vacíos (Task 3), integración en la grilla (Task 4), verificación manual de permisos y navegación (Task 5). Fuera de alcance (StatusBarChart, paginación) no se tocan.
- **Placeholders**: ninguno — todos los pasos incluyen código completo y comandos exactos.
- **Consistencia de tipos/nombres**: `getSeverityItems(severity, type)` se usa igual en `api/dashboard.js`, `useSeverityItems.js` y los tests; claves de cache `${severity}-${type}` consistentes entre hook y componente (`itemsByKey['1-risk']`); `SeverityItem{id,title,status}` consistente entre schema Pydantic y los datos mockeados en frontend.
