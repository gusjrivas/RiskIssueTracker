# Dashboard Severity Drawer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the per-cell 3D flip (PR #48) with a single full-width "drawer" below the severity matrix: clicking any of the 9 cells toggles a list of all visible risks/issues grouped by severity (1→9), each linking directly to `/risks/{id}` or `/issues/{id}`.

**Architecture:** New backend endpoint `GET /api/v1/dashboard/stats/severity-items` returns everything grouped by severity in one call (reusing `_visibility_clause`). Frontend gets a new lazy hook `useSeverityGroups` (called from the page), a new presentational `SeverityDrawer` component, and `SeverityMatrixGrid` goes back to simple cells that just toggle the drawer open/closed. All code from the per-cell flip (`SeverityCellFlip`, `useSeverityItems`, old endpoint/schemas) is removed.

**Tech Stack:** FastAPI + SQLAlchemy + Pydantic v2 (backend), React + Vite + Tailwind + React Router + Vitest/Testing Library (frontend).

**Spec:** `docs/superpowers/specs/2026-06-14-dashboard-severity-drawer.md`

---

### Task 1: Backend — grouped severity-items endpoint

**Files:**
- Modify: `backend/app/schemas/dashboard.py`
- Modify: `backend/app/services/dashboard_service.py`
- Modify: `backend/app/api/dashboard.py`
- Modify: `backend/tests/integration/api/test_dashboard.py`

This task replaces `GET /stats/severity/{severity}?type=` (and its schemas/service/tests) with `GET /stats/severity-items`, which returns ALL risks/issues visible to the current user, grouped by severity 1–9 (only severities with at least one item), risks before issues within each group, each subset ordered by title.

- [ ] **Step 1: Replace the old test class with the new one (failing)**

In `backend/tests/integration/api/test_dashboard.py`, **delete** the `_get_severity_items` helper function and the entire `TestSeverityItems` class (currently lines 187–256, everything from `def _get_severity_items_helper...` through the end of the file). In their place, append the following at the end of the file:

```python
def _get_severity_items_grouped(client, token):
    return client.get(
        "/api/v1/dashboard/stats/severity-items",
        headers={"Authorization": f"Bearer {token}"},
    )


# ---------------------------------------------------------------------------
# GET /dashboard/stats/severity-items
# ---------------------------------------------------------------------------

class TestSeverityItemsGrouped:
    def test_requires_auth(self, client):
        resp = client.get("/api/v1/dashboard/stats/severity-items")
        assert resp.status_code in (401, 403)

    def test_admin_sees_all_grouped_by_severity(self, client, admin_token, seed):
        resp = _get_severity_items_grouped(client, admin_token)
        assert resp.status_code == 200
        groups = resp.json()["groups"]

        severities = [g["severity"] for g in groups]
        assert severities == [1, 3, 4, 5, 9]

        group1 = next(g for g in groups if g["severity"] == 1)
        assert len(group1["items"]) == 2
        assert all(i["type"] == "risk" for i in group1["items"])
        assert all(i["title"] == "Risk sev 1" for i in group1["items"])

        group9 = next(g for g in groups if g["severity"] == 9)
        assert len(group9["items"]) == 1
        assert group9["items"][0]["title"] == "Issue sev 9"
        assert group9["items"][0]["status"] == "closed"
        assert group9["items"][0]["type"] == "issue"

    def test_group_orders_risks_before_issues(self, client, admin_token, seed):
        resp = _get_severity_items_grouped(client, admin_token)
        group4 = next(g for g in resp.json()["groups"] if g["severity"] == 4)
        assert [i["type"] for i in group4["items"]] == ["risk", "issue"]
        assert group4["items"][0]["title"] == "Risk sev 4"
        assert group4["items"][0]["status"] == "derived"
        assert group4["items"][1]["title"] == "Issue sev 4"
        assert group4["items"][1]["status"] == "in_progress"

    def test_regular_user_sees_only_visible(self, client, user_token, seed):
        resp = _get_severity_items_grouped(client, user_token)
        assert resp.status_code == 200
        groups = resp.json()["groups"]

        severities = [g["severity"] for g in groups]
        assert severities == [1, 3, 4]

        group1 = next(g for g in groups if g["severity"] == 1)
        assert len(group1["items"]) == 1
        assert group1["items"][0]["type"] == "risk"

        group4 = next(g for g in groups if g["severity"] == 4)
        assert [i["type"] for i in group4["items"]] == ["risk", "issue"]

    def test_severities_without_visible_items_are_omitted(self, client, admin_token, seed):
        resp = _get_severity_items_grouped(client, admin_token)
        severities = [g["severity"] for g in resp.json()["groups"]]
        # severidad 2 solo tiene el risk soft-deleted -> no aparece
        assert 2 not in severities
        assert 6 not in severities
        assert 7 not in severities
        assert 8 not in severities

    def test_empty_db_returns_no_groups(self, client, admin_token):
        resp = _get_severity_items_grouped(client, admin_token)
        assert resp.status_code == 200
        assert resp.json()["groups"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run (from `backend/`): `python -m pytest tests/integration/api/test_dashboard.py -v`

Expected: the 6 new `TestSeverityItemsGrouped` tests FAIL with 404 (route `/stats/severity-items` doesn't exist yet). No `TestSeverityItems` tests remain.

- [ ] **Step 3: Replace the schemas**

In `backend/app/schemas/dashboard.py`, replace the entire file content with:

```python
import uuid

from pydantic import BaseModel

from app.schemas.common import EntityType


class EntityStats(BaseModel):
    total: int
    # Claves de severidad "1".."9" como string (JSON no admite claves int),
    # siempre zero-filled para que el frontend no necesite defaults.
    by_severity: dict[str, int]
    by_status: dict[str, int]


class DashboardStatsResponse(BaseModel):
    risks: EntityStats
    issues: EntityStats


class SeverityGroupItem(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    type: EntityType


class SeverityGroup(BaseModel):
    severity: int
    items: list[SeverityGroupItem]


class SeverityItemsGroupedResponse(BaseModel):
    groups: list[SeverityGroup]
```

- [ ] **Step 4: Replace the service function**

In `backend/app/services/dashboard_service.py`:

1. Replace the import block:

```python
from app.schemas.dashboard import (
    DashboardStatsResponse,
    EntityStats,
    SeverityItem,
    SeverityItemsResponse,
)
```

with:

```python
from app.schemas.dashboard import (
    DashboardStatsResponse,
    EntityStats,
    SeverityGroup,
    SeverityGroupItem,
    SeverityItemsGroupedResponse,
)
```

2. Replace the existing `get_severity_items` function (the whole function, at the end of the file) with:

```python
def get_severity_groups(db: Session, current_user: User) -> SeverityItemsGroupedResponse:
    groups: list[SeverityGroup] = []

    for severity in range(1, 10):
        items: list[SeverityGroupItem] = []

        for model, entity_type in ((Risk, EntityType.risk), (Issue, EntityType.issue)):
            conditions = [model.deleted_at.is_(None), model.severity == severity]
            visibility = _visibility_clause(model, current_user)
            if visibility is not None:
                conditions.append(visibility)

            rows = db.execute(
                select(model.id, model.title, model.status)
                .where(*conditions)
                .order_by(model.title)
            ).all()

            items.extend(
                SeverityGroupItem(
                    id=row.id, title=row.title, status=row.status.value, type=entity_type
                )
                for row in rows
            )

        if items:
            groups.append(SeverityGroup(severity=severity, items=items))

    return SeverityItemsGroupedResponse(groups=groups)
```

- [ ] **Step 5: Replace the router endpoint**

Replace the entire content of `backend/app/api/dashboard.py` with:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import DashboardStatsResponse, SeverityItemsGroupedResponse
from app.services import dashboard_service
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_stats(db, current_user)


@router.get("/stats/severity-items", response_model=SeverityItemsGroupedResponse)
def get_severity_items_grouped(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_severity_groups(db, current_user)
```

- [ ] **Step 6: Run tests to verify they pass**

Run (from `backend/`): `python -m pytest tests/integration/api/test_dashboard.py -v`

Expected: all tests in `test_dashboard.py` PASS (`TestDashboardStats` + `TestSeverityItemsGrouped`, 11 tests total).

Then run the full backend suite: `python -m pytest -q`

Expected: all tests PASS (no other module referenced the removed `SeverityItem`/`SeverityItemsResponse`/`get_severity_items`/old route).

- [ ] **Step 7: Commit**

```bash
git add backend/app/schemas/dashboard.py backend/app/services/dashboard_service.py backend/app/api/dashboard.py backend/tests/integration/api/test_dashboard.py
git commit -m "feat: endpoint agrupado de severidad para la bandeja del dashboard"
```

---

### Task 2: Frontend — `getSeverityGroups` API call + `useSeverityGroups` hook

**Files:**
- Modify: `frontend/src/api/dashboard.js`
- Create: `frontend/src/hooks/useSeverityGroups.js`
- Create: `frontend/src/__tests__/hooks/useSeverityGroups.test.jsx`

This task only ADDS new code (it does not remove `getSeverityItems`/`useSeverityItems` yet — that happens in Task 4 once nothing references them). `useSeverityGroups` is **lazy**: it does not fetch on mount, only when `fetchGroups()` is called (the first time the drawer opens), and only fetches once.

- [ ] **Step 1: Write the failing hook test**

Create `frontend/src/__tests__/hooks/useSeverityGroups.test.jsx`:

```jsx
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useSeverityGroups } from '../../hooks/useSeverityGroups'
import * as dashboardApi from '../../api/dashboard'

vi.mock('../../api/dashboard')

describe('useSeverityGroups', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('no hace fetch hasta que se llama fetchGroups', () => {
    dashboardApi.getSeverityGroups.mockResolvedValue({ groups: [] })
    renderHook(() => useSeverityGroups())

    expect(dashboardApi.getSeverityGroups).not.toHaveBeenCalled()
  })

  it('carga los groups y los expone en data', async () => {
    const groups = [{ severity: 1, items: [{ id: 'r1', title: 'Risk 1', status: 'open', type: 'risk' }] }]
    dashboardApi.getSeverityGroups.mockResolvedValue({ groups })
    const { result } = renderHook(() => useSeverityGroups())

    await act(async () => {
      await result.current.fetchGroups()
    })

    expect(result.current.data).toEqual(groups)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('no vuelve a pedir datos si fetchGroups se llama de nuevo (cache)', async () => {
    dashboardApi.getSeverityGroups.mockResolvedValue({ groups: [] })
    const { result } = renderHook(() => useSeverityGroups())

    await act(async () => {
      await result.current.fetchGroups()
    })
    await act(async () => {
      await result.current.fetchGroups()
    })

    expect(dashboardApi.getSeverityGroups).toHaveBeenCalledTimes(1)
  })

  it('expone error si la API falla y permite reintentar', async () => {
    dashboardApi.getSeverityGroups.mockRejectedValueOnce(new Error('boom'))
    dashboardApi.getSeverityGroups.mockResolvedValueOnce({ groups: [] })
    const { result } = renderHook(() => useSeverityGroups())

    await act(async () => {
      await result.current.fetchGroups()
    })
    expect(result.current.error).toBe('boom')
    expect(result.current.loading).toBe(false)

    await act(async () => {
      await result.current.fetchGroups()
    })
    expect(dashboardApi.getSeverityGroups).toHaveBeenCalledTimes(2)
    expect(result.current.error).toBeNull()
    expect(result.current.data).toEqual([])
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `frontend/`): `npx vitest run src/__tests__/hooks/useSeverityGroups.test.jsx`

Expected: FAIL — `useSeverityGroups` and `getSeverityGroups` don't exist yet (module not found).

- [ ] **Step 3: Add `getSeverityGroups` to the API module**

In `frontend/src/api/dashboard.js`, add a new export (keep the existing ones for now):

```js
export const getSeverityGroups = () =>
  apiGet('/api/v1/dashboard/stats/severity-items')
```

- [ ] **Step 4: Implement the hook**

Create `frontend/src/hooks/useSeverityGroups.js`:

```js
import { useState, useCallback, useRef } from 'react'
import * as dashboardApi from '../api/dashboard'

// Hook lazy: no pide datos hasta que se llama fetchGroups() (al abrir la
// bandeja por primera vez), y luego cachea el resultado.
export function useSeverityGroups() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const fetched = useRef(false)

  const fetchGroups = useCallback(async () => {
    if (fetched.current) return
    fetched.current = true
    setLoading(true)
    try {
      const res = await dashboardApi.getSeverityGroups()
      setData(res.groups)
      setError(null)
    } catch (e) {
      setError(e.message)
      fetched.current = false
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, fetchGroups }
}
```

- [ ] **Step 5: Run test to verify it passes**

Run (from `frontend/`): `npx vitest run src/__tests__/hooks/useSeverityGroups.test.jsx`

Expected: all 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/dashboard.js frontend/src/hooks/useSeverityGroups.js frontend/src/__tests__/hooks/useSeverityGroups.test.jsx
git commit -m "feat: hook useSeverityGroups y api getSeverityGroups"
```

---

### Task 3: Frontend — `SeverityDrawer` component

**Files:**
- Create: `frontend/src/components/SeverityDrawer.jsx`
- Create: `frontend/src/__tests__/components/SeverityDrawer.test.jsx`

`SeverityDrawer` is a pure presentational component (no hooks, no fetch — receives everything via props), per `.claude/rules/frontend.md`. It renders nothing when `open` is `false`. When `open` is `true`, it shows loading/error/empty states, or the list of severity groups (each with a `SeverityBadge` header and a list of `Link`s mixing risks and issues, each with a type label and `StatusBadge`).

- [ ] **Step 1: Write the failing component test**

Create `frontend/src/__tests__/components/SeverityDrawer.test.jsx`:

```jsx
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import SeverityDrawer from '../../components/SeverityDrawer'

function renderDrawer(props = {}) {
  return render(
    <MemoryRouter>
      <SeverityDrawer open={true} groups={null} loading={false} error={null} {...props} />
    </MemoryRouter>
  )
}

describe('SeverityDrawer', () => {
  it('no renderiza nada si open es false', () => {
    renderDrawer({ open: false })
    expect(screen.queryByTestId('severity-drawer')).not.toBeInTheDocument()
  })

  it('muestra "Cargando..." mientras loading es true', () => {
    renderDrawer({ loading: true })
    expect(screen.getByTestId('severity-drawer')).toHaveTextContent('Cargando...')
  })

  it('muestra un mensaje de error', () => {
    renderDrawer({ error: 'boom' })
    expect(screen.getByText('Error al cargar.')).toBeInTheDocument()
  })

  it('muestra mensaje cuando no hay grupos', () => {
    renderDrawer({ groups: [] })
    expect(screen.getByText('No hay riesgos ni issues para mostrar.')).toBeInTheDocument()
  })

  it('renderiza grupos por severidad con links a riesgos e issues', () => {
    renderDrawer({
      groups: [
        {
          severity: 1,
          items: [
            { id: 'r1', title: 'Riesgo crítico', status: 'open', type: 'risk' },
            { id: 'i1', title: 'Issue crítico', status: 'closed', type: 'issue' },
          ],
        },
        {
          severity: 3,
          items: [
            { id: 'r2', title: 'Riesgo medio', status: 'in_progress', type: 'risk' },
          ],
        },
      ],
    })

    expect(screen.getByTestId('severity-group-1')).toBeInTheDocument()
    expect(screen.getByTestId('severity-group-3')).toBeInTheDocument()

    const riskLink = screen.getByRole('link', { name: /Riesgo crítico/ })
    expect(riskLink).toHaveAttribute('href', '/risks/r1')

    const issueLink = screen.getByRole('link', { name: /Issue crítico/ })
    expect(issueLink).toHaveAttribute('href', '/issues/i1')

    expect(screen.getAllByTestId('severity-badge')).toHaveLength(2)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `frontend/`): `npx vitest run src/__tests__/components/SeverityDrawer.test.jsx`

Expected: FAIL — `frontend/src/components/SeverityDrawer.jsx` does not exist.

- [ ] **Step 3: Implement the component**

Create `frontend/src/components/SeverityDrawer.jsx`:

```jsx
import { Link } from 'react-router-dom'
import SeverityBadge from './SeverityBadge'
import StatusBadge from './StatusBadge'

const TYPE_LABELS = { risk: 'Riesgo', issue: 'Issue' }
const BASE_PATHS = { risk: '/risks', issue: '/issues' }

// Bandeja única debajo de la matriz de severidad: lista todos los
// riesgos/issues visibles para el usuario, agrupados por severidad
// (1 = más crítico, primero). Puramente presentacional: recibe todo por
// props, sin fetch propio.
export default function SeverityDrawer({ groups, loading, error, open }) {
  if (!open) return null

  return (
    <div data-testid="severity-drawer" className="card mt-2 space-y-4">
      {loading ? (
        <p className="text-sm text-muted">Cargando...</p>
      ) : error ? (
        <p className="text-sm text-red-500">Error al cargar.</p>
      ) : !groups || groups.length === 0 ? (
        <p className="text-sm text-muted">No hay riesgos ni issues para mostrar.</p>
      ) : (
        groups.map(group => (
          <div key={group.severity} data-testid={`severity-group-${group.severity}`}>
            <SeverityBadge severity={group.severity} />
            <div className="mt-2 space-y-1.5">
              {group.items.map(item => (
                <Link
                  key={`${item.type}-${item.id}`}
                  to={`${BASE_PATHS[item.type]}/${item.id}`}
                  className="flex flex-wrap items-center justify-between gap-2 text-sm hover:underline"
                >
                  <span className="flex items-center gap-2 min-w-0">
                    <span className="text-[10px] uppercase text-muted shrink-0">
                      {TYPE_LABELS[item.type]}
                    </span>
                    <span className="truncate">{item.title}</span>
                  </span>
                  <StatusBadge status={item.status} />
                </Link>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

Run (from `frontend/`): `npx vitest run src/__tests__/components/SeverityDrawer.test.jsx`

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/SeverityDrawer.jsx frontend/src/__tests__/components/SeverityDrawer.test.jsx
git commit -m "feat: componente SeverityDrawer (bandeja de riesgos/issues por severidad)"
```

---

### Task 4: Frontend — wire up the drawer in `SeverityMatrixGrid` + `DashboardStatsPage`, remove the old flip code

**Files:**
- Modify: `frontend/src/components/SeverityMatrixGrid.jsx`
- Modify: `frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx`
- Modify: `frontend/src/pages/DashboardStatsPage.jsx`
- Delete: `frontend/src/components/SeverityCellFlip.jsx`
- Delete: `frontend/src/__tests__/components/SeverityCellFlip.test.jsx`
- Delete: `frontend/src/hooks/useSeverityItems.js`
- Delete: `frontend/src/__tests__/hooks/useSeverityItems.test.jsx`
- Modify: `frontend/src/api/dashboard.js` (remove `getSeverityItems`)

This is the integration task: the 9 matrix cells go back to being simple buttons (counts + severity number, no flip), any cell click toggles the single `SeverityDrawer` open/closed (calling `onOpenDrawer` — i.e. `fetchGroups` — only the first time it opens), and `DashboardStatsPage` wires `useSeverityGroups` (called at page level, per `.claude/rules/frontend.md`) into `SeverityMatrixGrid` via props. All code from the old per-cell flip becomes unused after this task and is deleted in the same task (so the full suite stays green throughout — nothing references the deleted files anymore once this task is done).

- [ ] **Step 1: Replace `SeverityMatrixGrid.test.jsx` with the new expectations (failing)**

Replace the entire content of `frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx` with:

```jsx
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import SeverityMatrixGrid from '../../components/SeverityMatrixGrid'

const risksBySeverity = { 1: 3, 2: 0, 3: 1, 4: 0, 5: 2, 6: 0, 7: 0, 8: 0, 9: 4 }
const issuesBySeverity = { 1: 1, 2: 0, 3: 0, 4: 5, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0 }

function renderGrid(props = {}) {
  const onOpenDrawer = vi.fn()
  const utils = render(
    <MemoryRouter>
      <SeverityMatrixGrid
        risksBySeverity={risksBySeverity}
        issuesBySeverity={issuesBySeverity}
        groups={null}
        groupsLoading={false}
        groupsError={null}
        onOpenDrawer={onOpenDrawer}
        {...props}
      />
    </MemoryRouter>
  )
  return { ...utils, onOpenDrawer }
}

describe('SeverityMatrixGrid', () => {
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
    renderGrid({ risksBySeverity: {}, issuesBySeverity: {} })
    expect(screen.getByTestId('matrix-cell-1')).toHaveTextContent('0 riesgos')
  })

  it('al hacer click en una celda abre la bandeja y llama a onOpenDrawer', () => {
    const { onOpenDrawer } = renderGrid({
      groups: [{ severity: 1, items: [{ id: 'r1', title: 'Riesgo A', status: 'open', type: 'risk' }] }],
    })

    expect(screen.queryByTestId('severity-drawer')).not.toBeInTheDocument()

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    expect(onOpenDrawer).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('severity-drawer')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Riesgo A/ })).toHaveAttribute('href', '/risks/r1')
  })

  it('un segundo click en cualquier celda cierra la bandeja sin volver a llamar onOpenDrawer', () => {
    const { onOpenDrawer } = renderGrid({ groups: [] })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))
    expect(screen.getByTestId('severity-drawer')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('matrix-cell-5'))
    expect(screen.queryByTestId('severity-drawer')).not.toBeInTheDocument()
    expect(onOpenDrawer).toHaveBeenCalledTimes(1)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run (from `frontend/`): `npx vitest run src/__tests__/components/SeverityMatrixGrid.test.jsx`

Expected: FAIL — current `SeverityMatrixGrid` renders `SeverityCellFlip` cells (flip-back testids, different click behavior, no `onOpenDrawer`/`groups` props handling).

- [ ] **Step 3: Rewrite `SeverityMatrixGrid.jsx`**

Replace the entire content of `frontend/src/components/SeverityMatrixGrid.jsx` with:

```jsx
import { useState } from 'react'
import { SEVERITY_MATRIX, PROXIMITY_LABELS, ZONE_LABELS } from '../utils/severityCalc'
import { severityClass } from './SeverityBadge'
import SeverityDrawer from './SeverityDrawer'

const ZONES = ['bajo', 'medio', 'alto']

function plural(n, singular, pluralForm) {
  return `${n} ${n === 1 ? singular : pluralForm}`
}

// Grilla 3×3 de la matriz de severidad (proximidad × zona de exposición).
// Cada celda corresponde a un único valor de severidad 1-9 (la matriz es
// biyectiva). Cualquier celda hace toggle de la bandeja única (SeverityDrawer)
// debajo de la grilla, que lista todos los riesgos/issues agrupados por
// severidad.
export default function SeverityMatrixGrid({
  risksBySeverity = {},
  issuesBySeverity = {},
  groups,
  groupsLoading,
  groupsError,
  onOpenDrawer,
}) {
  const [open, setOpen] = useState(false)

  const toggleDrawer = () => {
    if (!open) onOpenDrawer()
    setOpen(o => !o)
  }

  return (
    <div>
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
              const risks = risksBySeverity[sev] ?? 0
              const issues = issuesBySeverity[sev] ?? 0
              return (
                <button
                  key={zone}
                  type="button"
                  onClick={toggleDrawer}
                  data-testid={`matrix-cell-${sev}`}
                  className={`${severityClass(sev)} relative flex flex-col items-center justify-center gap-1.5 py-6 px-3 w-full`}
                >
                  <span className="font-display text-2xl font-bold leading-none">
                    {plural(risks, 'riesgo', 'riesgos')}
                  </span>
                  <span className="font-display text-lg font-semibold leading-none opacity-75">
                    {plural(issues, 'issue', 'issues')}
                  </span>
                  <span
                    data-testid={`matrix-sev-${sev}`}
                    className="absolute bottom-1.5 left-2 text-[10px] font-medium opacity-50 leading-none"
                  >
                    {sev}
                  </span>
                </button>
              )
            })}
          </div>
        ))}
      </div>

      <SeverityDrawer groups={groups} loading={groupsLoading} error={groupsError} open={open} />
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

Run (from `frontend/`): `npx vitest run src/__tests__/components/SeverityMatrixGrid.test.jsx`

Expected: all 8 tests PASS.

- [ ] **Step 5: Wire `useSeverityGroups` into `DashboardStatsPage.jsx`**

In `frontend/src/pages/DashboardStatsPage.jsx`:

1. Add the import:

```js
import { useSeverityGroups } from '../hooks/useSeverityGroups'
```

2. Inside the component, after the existing `useDashboardStats` call, add:

```js
const { data: severityGroups, loading: groupsLoading, error: groupsError, fetchGroups } = useSeverityGroups()
```

3. Update the `<SeverityMatrixGrid ... />` usage to pass the new props:

```jsx
<SeverityMatrixGrid
  risksBySeverity={data.risks.by_severity}
  issuesBySeverity={data.issues.by_severity}
  groups={severityGroups}
  groupsLoading={groupsLoading}
  groupsError={groupsError}
  onOpenDrawer={fetchGroups}
/>
```

- [ ] **Step 6: Delete the old per-cell flip code**

```bash
git rm frontend/src/components/SeverityCellFlip.jsx
git rm frontend/src/__tests__/components/SeverityCellFlip.test.jsx
git rm frontend/src/hooks/useSeverityItems.js
git rm frontend/src/__tests__/hooks/useSeverityItems.test.jsx
```

- [ ] **Step 7: Remove `getSeverityItems` from the API module**

In `frontend/src/api/dashboard.js`, remove the `getSeverityItems` export, leaving:

```js
import { apiGet } from './client'

export const getDashboardStats = () => apiGet('/api/v1/dashboard/stats')

export const getSeverityGroups = () =>
  apiGet('/api/v1/dashboard/stats/severity-items')
```

- [ ] **Step 8: Run the full frontend suite**

Run (from `frontend/`): `npx vitest run`

Expected: all tests PASS (no remaining references to `SeverityCellFlip`, `useSeverityItems`, or `getSeverityItems`).

- [ ] **Step 9: Commit**

```bash
git add frontend/src/components/SeverityMatrixGrid.jsx frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx frontend/src/pages/DashboardStatsPage.jsx frontend/src/api/dashboard.js
git add frontend/src/components/SeverityCellFlip.jsx frontend/src/__tests__/components/SeverityCellFlip.test.jsx frontend/src/hooks/useSeverityItems.js frontend/src/__tests__/hooks/useSeverityItems.test.jsx
git commit -m "feat: bandeja unica de severidad en SeverityMatrixGrid, elimina flip por celda"
```

---

### Task 5: Manual end-to-end verification (desktop + mobile)

**Files:** none (verification only — no code changes, no commit)

Using the running docker-compose dev environment (hot-reload, no rebuild needed) and Playwright MCP:

- [ ] **Step 1:** Log in as admin (`admin@test.com` / `Admin1234!`) and navigate to `/dashboard`.
- [ ] **Step 2:** Click any severity cell. Verify the drawer appears below the 3×3 grid, showing severity groups ordered 1→9 (only non-empty groups), each item showing type label, title, and `StatusBadge`.
- [ ] **Step 3:** Click a risk link and an issue link from the drawer (in separate passes), verify navigation to `/risks/{id}` and `/issues/{id}` respectively, then navigate back to `/dashboard`.
- [ ] **Step 4:** Click any cell again (drawer open) and verify the drawer closes (toggle).
- [ ] **Step 5:** Resize the browser to a mobile viewport (e.g. 375×812) and repeat steps 2–4, verifying the drawer is fully readable, items wrap instead of overflowing, and the matrix remains usable above it.
- [ ] **Step 6:** Take a screenshot of the open drawer on both desktop and mobile viewports for the record.

If any issue is found, fix it with a small follow-up commit (TDD: add/adjust a test first if the fix changes component behavior) before moving to Task 6.

---

### Task 6: Document this iteration in `.claude/prompts/27_prompt_dashboard-stats.md`

**Files:**
- Modify: `.claude/prompts/27_prompt_dashboard-stats.md`

This file documents Prompt 27 (the original dashboard feature, PR #43) with sections: Contexto, Branch, Prompts, Decisiones de diseño, Implementación, Tests, Verificación en vivo, Resultado. Keep all existing content unchanged, and append a new top-level section at the end of the file documenting this iteration (the severity drill-down: first the per-cell flip from PR #48/branch `feature/dashboard-severity-drilldown`, then this replacement with the single drawer).

- [ ] **Step 1: Append the new section**

Append to the end of `backend/../.claude/prompts/27_prompt_dashboard-stats.md` (i.e. `.claude/prompts/27_prompt_dashboard-stats.md`):

```markdown

---

# Iteración 2 — Drill-down de severidad: de flip por celda a bandeja única

## Contexto
El dashboard de Prompt 27 mostraba solo conteos por celda de la matriz de
severidad. Se pidió poder ver el detalle (riesgos/issues) desde cada celda,
con link directo a la página de detalle.

## Branch
`feature/dashboard-severity-drilldown` → PR #48 (primera iteración, flip por
celda) + commits adicionales (segunda iteración, bandeja única)

## Prompts

```
[pegar aquí el prompt original que pidió el flip 3D por celda con listas de
riesgos/issues, según el historial de la conversación de PR #48]
```

```
no es user frendly la implementación. Vamos a realizar la siguiente mejora.
1 cuando se toque una card del dashboard toda la zona del dashboard se debe
comvertir en una bandeja donde se vean los riesgos y problemas en una lista
de links ( como sifuera una bandeja) agrupados por severidad ( es decir los
de mayor severidad 1 al principio y los mas bajos 9 al final). EL componente
tiene que poder visualizarse bien en un movil. Mantener el tema de que cada
usuario pueda ver sus riesgos y problemas de acuerdo a sus persmisos, salvo
el admin que puede ver todo. Todo este desarrollo mantengamoslo en el actual
branch dashboar-severity-drilldown
```

```
la opcion A me parece la mejor solo que hay que incorporar que se oculta la
bandeja al volver hacer click en la matriz. es decir que el usuario tenga la
opcion de desplegar la bandeja para luego presional un link de la lista para
ir directo a la página del riesgo o problemas
```

## Decisiones de diseño (brainstorming aprobado)

- **Primera iteración (PR #48, descartada):** cada celda de la matriz hacía
  flip 3D y mostraba en el reverso una mini-lista de riesgos/issues de esa
  severidad+tipo (`SeverityCellFlip`, hook `useSeverityItems`, endpoint
  `GET /stats/severity/{severity}?type=`). Resultó poco usable, sobre todo
  en mobile (espacio muy reducido por celda).
- **Segunda iteración (actual):** se eligió, entre 3 layouts presentados con
  el companion visual (panel debajo de la matriz / reemplazo total / hoja
  deslizante), el **panel debajo de la matriz** (Opción A), con la mejora
  pedida por el usuario de que cualquier celda funcione como **toggle**
  (abre/cierra la misma bandeja).
- La bandeja muestra **siempre el listado completo** (severidades 1-9, todas
  las que tengan items visibles para el usuario), sin filtrar por la celda
  clickeada — la celda es solo el disparador.
- Dentro de cada grupo de severidad, riesgos e issues se **mezclan en una
  sola lista** (riesgos primero, luego issues, cada subset ordenado por
  título), con una etiqueta de tipo + `StatusBadge` + link directo.
- Severidades sin items visibles **no aparecen** en la respuesta/bandeja.
- Todo el código de la primera iteración (`SeverityCellFlip`,
  `useSeverityItems`, endpoint por severidad+tipo) se eliminó por completo
  (YAGNI) y se reemplazó por un único endpoint que devuelve todo agrupado.
- Para cumplir `.claude/rules/frontend.md` (hooks solo en páginas,
  componentes reciben props), `useSeverityGroups` se llama desde
  `DashboardStatsPage` y se pasa por props a `SeverityMatrixGrid` →
  `SeverityDrawer` (puramente presentacional).

## Implementación

### Backend
- `GET /api/v1/dashboard/stats/severity-items` → `{ groups: [{ severity, items: [{ id, title, status, type }] }] }`,
  reemplaza `GET /stats/severity/{severity}?type=`.
- `app/services/dashboard_service.py`: `get_severity_groups` reutiliza
  `_visibility_clause` sin cambios; itera severidades 1-9, consulta Risk e
  Issue (excluyendo soft-deleted), omite severidades sin items, ordena
  risks antes que issues (por título) dentro de cada grupo.
- Nuevos schemas `SeverityGroupItem`, `SeverityGroup`,
  `SeverityItemsGroupedResponse` (reemplazan `SeverityItem`/`SeverityItemsResponse`).

### Frontend
- `api/dashboard.js`: `getSeverityGroups()` (reemplaza `getSeverityItems`).
- `hooks/useSeverityGroups.js`: hook lazy `{ data, loading, error, fetchGroups }`,
  llamado desde `DashboardStatsPage`.
- `components/SeverityDrawer.jsx` (nuevo): bandeja presentacional, agrupa por
  severidad con `SeverityBadge` + links (`/risks/{id}` o `/issues/{id}`) con
  etiqueta de tipo y `StatusBadge`.
- `components/SeverityMatrixGrid.jsx`: vuelve a celdas simples (sin flip);
  cualquier celda hace toggle de `SeverityDrawer` debajo de la grilla.
- Eliminados: `SeverityCellFlip.jsx`, `useSeverityItems.js` y sus tests.

## Tests
- Backend: `TestSeverityItemsGrouped` (reemplaza `TestSeverityItems`) — auth,
  agrupado y ordenado por severidad, risks antes que issues, visibilidad por
  rol, severidades sin items omitidas, DB vacía. Suite completa: **[completar
  con el resultado real, ej. 388 passed]**.
- Frontend: `useSeverityGroups.test.jsx`, `SeverityDrawer.test.jsx`,
  `SeverityMatrixGrid.test.jsx` actualizado. Suite completa: **[completar con
  el resultado real]**.
- TDD: rojo → implementación → verde en cada tarea.

## Verificación en vivo (Docker Compose + Playwright MCP)
- Login admin → `/dashboard`: click en cualquier celda abre la bandeja con
  todas las severidades visibles (1→9, solo las no vacías), links a
  `/risks/{id}` y `/issues/{id}` funcionando, segundo click cierra la
  bandeja.
- Verificado en viewport mobile (375×812): la bandeja se lee correctamente,
  los items hacen wrap sin overflow.

## Resultado
La bandeja única reemplaza el flip por celda: más usable, especialmente en
mobile, y con una sola llamada al backend para traer todo el detalle
agrupado por severidad.
```

> **Nota para quien ejecute esta tarea:** completar los resultados reales de los tests (`X passed`) y, si el prompt original del PR #48 no está disponible en este contexto, recuperarlo del historial de la conversación o del PR #48 en GitHub antes de pegarlo en la sección "Prompts".

- [ ] **Step 2: Commit**

```bash
git add .claude/prompts/27_prompt_dashboard-stats.md
git commit -m "docs: documentar iteracion de bandeja unica de severidad en prompt 27"
```

---

## After all tasks

Use **superpowers:finishing-a-development-branch** (the branch already has an open PR #48 — pushing these new commits updates it automatically; offer to push).
