# Dashboard — Drill-down de severidad (flip cards) — Spec

**Fecha:** 2026-06-13
**Archivos a modificar/crear (backend):**
- `backend/app/schemas/dashboard.py` (nuevos schemas)
- `backend/app/services/dashboard_service.py` (nueva función + refactor de `_visibility_clause`)
- `backend/app/api/dashboard.py` (nuevo endpoint)
- `backend/tests/integration/api/test_dashboard.py` (nuevos tests)

**Archivos a modificar/crear (frontend):**
- `frontend/src/api/dashboard.js` (nueva función)
- `frontend/src/hooks/useSeverityItems.js` (nuevo hook)
- `frontend/src/components/SeverityCellFlip.jsx` (nuevo componente)
- `frontend/src/components/SeverityMatrixGrid.jsx` (usa el nuevo componente por celda)
- `frontend/src/__tests__/components/SeverityCellFlip.test.jsx` (nuevo)
- `frontend/src/__tests__/hooks/useSeverityItems.test.jsx` (nuevo)
- `frontend/src/__tests__/components/SeverityMatrixGrid.test.jsx` (actualizar)

---

## Objetivo

En el dashboard de estadísticas (`/dashboard`), cada celda de la matriz de severidad (`SeverityMatrixGrid`) muestra hoy solo conteos de riesgos e issues con esa severidad. Se agrega un comportamiento de **flip card**: al hacer click sobre una celda, esta se da vuelta y muestra un listado de links — uno por cada riesgo/issue con esa severidad — con título y estado (`StatusBadge`). Al hacer click en un link, el usuario navega directamente a la página de detalle de ese riesgo (`/risks/{id}`) o issue (`/issues/{id}`).

Los listados respetan la misma lógica de visibilidad que ya aplica `/dashboard/stats`: un admin ve todos los riesgos/issues; un user normal solo ve aquellos donde es *owner*, *creador*, o que pertenecen a un proyecto creado por él.

---

## Backend

### Endpoint nuevo

```
GET /api/v1/dashboard/stats/severity/{severity}?type=risk|issue
```

- **`severity`**: int, path param, debe estar en `1..9` → si está fuera de rango, FastAPI devuelve 422.
- **`type`**: `risk` | `issue`, query param obligatorio (enum) → valor inválido devuelve 422.
- **Auth**: requiere usuario autenticado (`Depends(get_current_user)`), igual que `/dashboard/stats`.

### Response

```json
{
  "items": [
    { "id": "uuid", "title": "Dada la falta de respaldo...", "status": "in_progress" }
  ]
}
```

- Lista vacía (`items: []`) si no hay riesgos/issues con esa severidad visibles para el usuario.
- Excluye entidades con `deleted_at IS NOT NULL` (mismo criterio que `/dashboard/stats`).
- Sin paginación — el volumen esperado por celda es bajo y el frontend maneja scroll interno.

### Schemas nuevos (`app/schemas/dashboard.py`)

```python
class SeverityItem(BaseModel):
    id: uuid.UUID
    title: str
    status: str  # valor del enum RiskStatus o IssueStatus, según `type`


class SeverityItemsResponse(BaseModel):
    items: list[SeverityItem]
```

### Service (`app/services/dashboard_service.py`)

- Refactor: extraer `_visibility_clause(model, current_user)` (ya existe) sin cambios — se reutiliza tal cual.
- Nueva función:

```python
def get_severity_items(
    db: Session, severity: int, entity_type: Literal["risk", "issue"], current_user: User
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
        items=[SeverityItem(id=r.id, title=r.title, status=r.status.value) for r in rows]
    )
```

### Router (`app/api/dashboard.py`)

```python
@router.get("/stats/severity/{severity}", response_model=SeverityItemsResponse)
def get_severity_items(
    severity: int = Path(ge=1, le=9),
    type: Literal["risk", "issue"] = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return dashboard_service.get_severity_items(db, severity, type, current_user)
```

> Nota: el query param se llama `type` (coincide con el lenguaje ya usado en `entity_type` de history). Internamente se mapea a `entity_type` al llamar al service.

---

## Frontend

### API (`frontend/src/api/dashboard.js`)

```js
export const getSeverityItems = (severity, type) =>
  apiGet(`/api/v1/dashboard/stats/severity/${severity}?type=${type}`)
```

### Hook (`frontend/src/hooks/useSeverityItems.js`)

- Expone `{ items, loading, error, fetchItems }`.
- `fetchItems(severity, type)`: si ya se cargó esa combinación `severity-type` (cache en memoria con `useRef`/`useState`), no vuelve a pedirla — devuelve los datos cacheados.
- Cache por celda: como cada celda tiene dos tipos (risk/issue), el hook se instancia una vez por celda y cachea ambos resultados.

### Componente `SeverityCellFlip.jsx`

Props: `sev` (severidad 1-9), `risksCount`, `issuesCount`.

- **Estado local**: `flipped` (bool).
- **Cara frontal** (contenido actual de la celda, sin cambios visuales): conteos de riesgos/issues + número de severidad en la esquina, envuelto en `<button onClick={() => setFlipped(true)}>`. Aplica a **todas** las celdas, incluso con 0 riesgos y 0 issues.
- **Cara trasera**:
  - Botón de cierre (ícono `X` o flecha, esquina superior) → `setFlipped(false)`.
  - Sección **"Riesgos"**: título de sección + lista de `<Link to={`/risks/${item.id}`}>` con `title` truncado y `<StatusBadge status={item.status} />`. Si vacío: `"No hay riesgos con esta severidad."`.
  - Sección **"Issues"**: igual, con `/issues/${item.id}` y estados de `IssueStatus`.
  - Ambas secciones dentro de un contenedor con `max-h-[Npx] overflow-y-auto` (scroll interno independiente).
  - Al pasar `flipped` a `true` por primera vez, dispara `fetchItems(sev, 'risk')` y `fetchItems(sev, 'issue')`.
- **Animación**: `framer-motion`, contenedor con `style={{ transformStyle: 'preserve-3d' }}`, `animate={{ rotateY: flipped ? 180 : 0 }}`. Cara frontal y trasera son hijos absolutos superpuestos con `backface-visibility: hidden`; la cara trasera tiene `rotateY: 180deg` fijo para quedar "del lado correcto" tras el flip.
- Mantiene el `data-testid="matrix-cell-{sev}"` y `data-testid="matrix-sev-{sev}"` existentes para no romper tests actuales; agrega `data-testid="matrix-cell-back-{sev}"` para la cara trasera.

### `SeverityMatrixGrid.jsx`

- Reemplaza el `<div>` de cada celda por `<SeverityCellFlip sev={sev} risksCount={risks} issuesCount={issues} />`.
- El resto de la grilla (labels de zona/proximidad) no cambia.

---

## Testing

### Backend (`tests/integration/api/test_dashboard.py`)

Casos nuevos para `GET /dashboard/stats/severity/{severity}?type=...`:
1. Admin ve todos los riesgos/issues de la severidad solicitada (de cualquier proyecto).
2. User normal solo ve los riesgos/issues donde es owner/creador/proyecto propio (replica fixtures ya usados para `/dashboard/stats`).
3. `severity=0` y `severity=10` → 422.
4. `type=foo` (inválido) → 422.
5. Severidad sin entidades visibles → `{"items": []}`.
6. Entidades con `deleted_at` no nulo no aparecen en el listado.

### Frontend

- **`useSeverityItems.test.jsx`**: fetch inicial llama a la API; segunda llamada con mismo `severity`+`type` no repite el fetch (mock contado); maneja error de red.
- **`SeverityCellFlip.test.jsx`**:
  - Render inicial muestra cara frontal con conteos.
  - Click → `flipped=true`, se renderiza cara trasera con `data-testid="matrix-cell-back-{sev}"`.
  - Items mockeados renderizan `<Link>` con `href="/risks/{id}"` / `href="/issues/{id}"` y `StatusBadge` correspondiente.
  - Secciones vacías muestran el mensaje "No hay riesgos/issues con esta severidad."
  - Click en botón de cierre vuelve a `flipped=false`.
- **`SeverityMatrixGrid.test.jsx`**: actualizar para verificar que cada celda renderiza `SeverityCellFlip` (smoke test, sin duplicar los casos de arriba).

---

## Fuera de alcance

- Flip en `StatusBarChart` (barras de estado) — explícitamente descartado para esta iteración.
- Paginación del listado dentro de la celda — se asume volumen bajo por severidad; scroll interno es suficiente.
- Edición/acciones desde la card volteada — solo navegación de lectura vía link.
