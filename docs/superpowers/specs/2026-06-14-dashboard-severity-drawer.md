# Dashboard — Bandeja única de severidad (reemplaza flip por celda) — Spec

**Fecha:** 2026-06-14
**Reemplaza:** la feature de flip 3D por celda (PR #48, branch `feature/dashboard-severity-drilldown`)

**Archivos a modificar/crear (backend):**
- `backend/app/schemas/dashboard.py` (reemplaza `SeverityItem`/`SeverityItemsResponse`)
- `backend/app/services/dashboard_service.py` (reemplaza `get_severity_items` por `get_severity_groups`)
- `backend/app/api/dashboard.py` (reemplaza el endpoint `/stats/severity/{severity}`)
- `backend/tests/integration/api/test_dashboard.py` (reemplaza `TestSeverityItems`)

**Archivos a modificar/crear (frontend):**
- `frontend/src/api/dashboard.js` (reemplaza `getSeverityItems` por `getSeverityGroups`)
- `frontend/src/hooks/useSeverityGroups.js` (nuevo, reemplaza `useSeverityItems.js`)
- `frontend/src/components/SeverityDrawer.jsx` (nuevo)
- `frontend/src/components/SeverityMatrixGrid.jsx` (vuelve a celdas simples + toggle de bandeja)
- `frontend/src/pages/DashboardStatsPage.jsx` (usa `useSeverityGroups`, pasa props)
- `frontend/src/__tests__/hooks/useSeverityGroups.test.jsx` (nuevo)
- `frontend/src/__tests__/components/SeverityDrawer.test.jsx` (nuevo)
- `frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx` (actualizar)

**Archivos a eliminar:**
- `frontend/src/components/SeverityCellFlip.jsx`
- `frontend/src/hooks/useSeverityItems.js`
- `frontend/src/__tests__/components/SeverityCellFlip.test.jsx`
- `frontend/src/api/dashboard.js`: función `getSeverityItems`
- `backend/app/schemas/dashboard.py`: `SeverityItem`, `SeverityItemsResponse`
- `backend/app/services/dashboard_service.py`: `get_severity_items`
- `backend/app/api/dashboard.py`: endpoint `GET /stats/severity/{severity}?type=`
- `backend/tests/integration/api/test_dashboard.py`: clase `TestSeverityItems`

---

## Objetivo

El flip 3D por celda (PR #48) no es user-friendly: cada celda es muy chica para mostrar listas, y no funciona bien en mobile. Se reemplaza por una **bandeja única** debajo de toda la matriz de severidad: al hacer click en **cualquier** celda, la bandeja se despliega mostrando **todos** los riesgos e issues visibles para el usuario, agrupados por severidad (1 = más crítico, primero; 9 = menos crítico, último). Un nuevo click en cualquier celda **oculta** la bandeja (toggle). Cada item es un link directo a `/risks/{id}` o `/issues/{id}`.

La visibilidad sigue la misma lógica que `/dashboard/stats`: admin ve todo, usuario regular solo ve lo que es owner/creador o de proyectos propios (`_visibility_clause`, sin cambios).

---

## Backend

### Endpoint nuevo

```
GET /api/v1/dashboard/stats/severity-items
```

- **Auth**: requiere usuario autenticado (`Depends(get_current_user)`), igual que `/dashboard/stats`.
- Sin parámetros.

### Response

```json
{
  "groups": [
    {
      "severity": 1,
      "items": [
        { "id": "uuid", "title": "Dada la falta de respaldo...", "status": "in_progress", "type": "risk" },
        { "id": "uuid", "title": "Caída del proveedor X",        "status": "open",        "type": "issue" }
      ]
    },
    {
      "severity": 3,
      "items": [ ... ]
    }
  ]
}
```

- `groups` solo incluye severidades (1–9) que tengan **al menos un item visible** para el usuario actual. Severidades sin items no aparecen.
- `groups` está ordenado por `severity` ascendente (1 → 9).
- Dentro de cada grupo, `items` contiene primero los `risk` (ordenados por `title`) y luego los `issue` (ordenados por `title`).
- Excluye entidades con `deleted_at IS NOT NULL` (mismo criterio que `/dashboard/stats`).
- `status` es el valor del enum `RiskStatus` o `IssueStatus` según `type`.

### Schemas (`app/schemas/dashboard.py`)

```python
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

Se eliminan `SeverityItem` y `SeverityItemsResponse`.

### Service (`app/services/dashboard_service.py`)

- `_visibility_clause` se reutiliza sin cambios.
- Nueva función:

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

Se elimina `get_severity_items`.

### Router (`app/api/dashboard.py`)

```python
@router.get("/stats/severity-items", response_model=SeverityItemsGroupedResponse)
def get_severity_items_grouped(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_severity_groups(db, current_user)
```

Se elimina el endpoint `GET /stats/severity/{severity}?type=`. Se eliminan también los imports que quedan sin uso (`Literal`, `Path`, `Query`, `EntityType` solo si ya no se usa — se sigue usando en el schema/service nuevo).

---

## Frontend

### API (`frontend/src/api/dashboard.js`)

```js
export const getSeverityGroups = () =>
  apiGet('/api/v1/dashboard/stats/severity-items')
```

Se elimina `getSeverityItems`.

### Hook (`frontend/src/hooks/useSeverityGroups.js`)

Mismo patrón que `useDashboardStats`, pero **lazy** (no fetch automático al montar — solo cuando se abre la bandeja por primera vez):

```js
import { useState, useCallback, useRef } from 'react'
import * as dashboardApi from '../api/dashboard'

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

Se elimina `useSeverityItems.js`.

### `pages/DashboardStatsPage.jsx`

- Llama `const { data: severityGroups, loading: groupsLoading, error: groupsError, fetchGroups } = useSeverityGroups()`.
- Pasa a `SeverityMatrixGrid`: `groups={severityGroups}`, `groupsLoading`, `groupsError`, `onOpenDrawer={fetchGroups}`.

### `components/SeverityMatrixGrid.jsx`

- Vuelve a celdas simples (sin flip, sin `SeverityCellFlip`): `<button>` con conteos grandes + número de severidad pequeño en la esquina, `data-testid="matrix-cell-{sev}"`, `data-testid="matrix-sev-{sev}"` (igual que antes del PR #48).
- Estado local `const [open, setOpen] = useState(false)`.
- `onClick` de **cualquier** celda: `if (!open) onOpenDrawer(); setOpen(o => !o)`.
- Debajo de la grilla 3×3, renderiza `<SeverityDrawer groups={groups} loading={groupsLoading} error={groupsError} open={open} />`.

### `components/SeverityDrawer.jsx` (nuevo)

Props: `groups` (array de `{severity, items}` o `null`), `loading`, `error`, `open`.

- Si `!open`, no renderiza nada (`return null`).
- Si `loading`, muestra `"Cargando..."`.
- Si `error`, muestra `"Error al cargar."` en rojo.
- Si `groups` vacío (`[]` o `null` tras cargar sin items), muestra `"No hay riesgos ni issues para mostrar."`.
- Si hay datos: por cada grupo (ya viene ordenado 1→9 y sin grupos vacíos desde el backend):
  - Header de sección con `<SeverityBadge severity={group.severity} />`.
  - Lista vertical de items: cada uno es un `<Link to={item.type === 'risk' ? `/risks/${item.id}` : `/issues/${item.id}`}>` con:
    - Etiqueta de tipo: texto pequeño `"Riesgo"` / `"Issue"` (`text-[10px] uppercase text-muted`).
    - Título truncado (`truncate`).
    - `<StatusBadge status={item.status} />`.
- Layout: bloque `w-full`, secciones apiladas verticalmente (`space-y-4` o similar), cada item en `flex items-center justify-between gap-2` con `flex-wrap` para que en mobile el badge de estado baje de línea si el título es largo. Sin `max-h`/scroll interno — es una sección normal de la página, full width, mobile-friendly por diseño (stack vertical).
- `data-testid="severity-drawer"` en el contenedor, `data-testid="severity-group-{severity}"` por sección.

---

## Testing

### Backend (`tests/integration/api/test_dashboard.py`)

Se elimina la clase `TestSeverityItems`. Nueva clase `TestSeverityItemsGrouped` para `GET /dashboard/stats/severity-items`:
1. Sin token → 401.
2. Admin ve `groups` con todos los riesgos/issues de cualquier proyecto, agrupados y ordenados por severidad ascendente.
3. User normal solo ve los riesgos/issues donde es owner/creador/proyecto propio (reutiliza fixtures de `/dashboard/stats`).
4. Severidades sin items visibles no aparecen en `groups`.
5. Dentro de un grupo, los `items` de tipo `risk` aparecen antes que los de tipo `issue`, cada subset ordenado por `title`.
6. Entidades con `deleted_at` no nulo no aparecen.
7. Sin ningún riesgo/issue visible → `{"groups": []}`.

### Frontend

- **`useSeverityGroups.test.jsx`**: no hace fetch hasta que se llama `fetchGroups()`; segunda llamada a `fetchGroups()` no repite el fetch (mock contado); maneja error de red (y permite reintentar tras error, ya que `fetched.current` se resetea).
- **`SeverityDrawer.test.jsx`**:
  - `open=false` → no renderiza nada.
  - `open=true, loading=true` → "Cargando...".
  - `open=true, error="..."` → "Error al cargar.".
  - `open=true, groups=[]` → "No hay riesgos ni issues para mostrar.".
  - `open=true, groups=[{severity:1, items:[...]}]` → renderiza `SeverityBadge`, links con `href` correcto según `type` (`/risks/{id}` o `/issues/{id}`), título y `StatusBadge`.
- **`SeverityMatrixGrid.test.jsx`**: click en una celda → llama `onOpenDrawer` una vez y muestra `SeverityDrawer` con `open=true`; segundo click en cualquier celda → `SeverityDrawer` con `open=false` (sin volver a llamar `onOpenDrawer`); las 9 celdas siguen mostrando conteos y número de severidad.

---

## Fuera de alcance

- Resaltar o hacer scroll automático hacia la severidad de la celda clickeada — la bandeja siempre muestra todo el listado completo igual, sin importar qué celda se clickeó.
- Paginación dentro de la bandeja — se asume volumen razonable; sin scroll interno limitado (a diferencia del diseño anterior).
- Edición/acciones desde la bandeja — solo navegación de lectura vía link.

---

## Tarea final (fuera del plan de implementación de código)

Al finalizar, actualizar `.claude/prompts/27_prompt_dashboard-stats.md`: mantener el contenido original (PR #43, dashboard inicial) y agregar al final una nueva sección documentando esta mejora (branch `feature/dashboard-severity-drilldown`, prompts del usuario para el flip y luego para la bandeja, decisiones de diseño, implementación y resultado), siguiendo el mismo formato que las secciones existentes.
