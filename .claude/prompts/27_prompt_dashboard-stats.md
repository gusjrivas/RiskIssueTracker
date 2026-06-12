# Prompt 27 — Feature: dashboard de riesgos e issues (matriz de severidad + estados)

## Contexto
La app gestionaba risks/issues por proyecto pero no tenía ninguna vista agregada.
Se pidió una página de dashboard con una grilla severidad × zona (celdas coloreadas
con counts) y un gráfico de cantidades por estado, con visibilidad por rol:
admin ve todo, usuario regular solo lo que le corresponde.

## Branch
`feature/dashboard-stats` → PR #43

## Prompts

```
vamos a empezar con una nueva feature hay que agregar a la aplicación una página que
será el dashboard de todos lo riesgos y problemas que se encuentran en el sistema se
deberá mostrar en una grilla en donde se visaulicen por severidad y por zona cada
cuadricula pintada del color que corresponde y dentro de ellas se reflejará la cantidad
en números de los risk o issues que esten en esa categoria. por otra parte se debe tener
otro grafico que indique la camtidad de riesgo y problemas en estado abierto en curso o
cerrados buscar la mejor manera de representarlos. El usuario administrador debe ver el
total de todos los risk y problemas de todos los proyectos. cada usuaior deberá ver los
dashbord con los risk y issue que le corresponden de acuerdo al proyecto al que están
asignados por el risk o issue. usa superpowers para empezar
```

```
levanta una version local para que la vea antes de aprobar el PR y el MR
```

```
hay que hacer que se vean mas grande la cantidad de risk o issue por cada caja y el
numero de la severidad tienen que verse pequeño sobre una esquina puede ser la
isquierda inferior de cada cajita es solo a modo informativo. hacer esa mejora antes
de seguir
```

```
mejora los colores de las barras de cantidad de abiertos cerrados en progreso para
que ses mas profesional
```

## Decisiones de diseño (plan mode aprobado)

- **Visibilidad sin tabla de membresía** (elección del usuario entre dos opciones):
  un usuario no-admin ve los risks/issues donde es `owner_id` o `created_by`, o de
  proyectos cuyo `created_by` es él. Admin ve todo.
- **Nueva ruta `/dashboard`** con link en el header; la home (lista de proyectos)
  queda como está.
- **La grilla 3×3 aprovecha que `SEVERITY_MATRIX` es biyectiva** (proximidad × zona
  → severidad 1–9 con 9 valores únicos): los issues, que solo tienen severity manual,
  se ubican en su celda por valor. El frontend arma la grilla con su matriz local;
  el backend devuelve solo counts.
- **Charts custom sin librería**: barras horizontales div + Tailwind + framer-motion,
  acorde al skill `ui-design-react.md`.
- Plugin `superpowers` instalado a pedido (no estaba disponible en la sesión; se usó
  plan mode como flujo equivalente).

## Implementación

### Backend
- `GET /api/v1/dashboard/stats` → `{ risks, issues }`, cada uno con `total`,
  `by_severity` (claves `"1".."9"` zero-filled) y `by_status` (enum completo
  zero-filled; risks incluye `derived`).
- `app/api/dashboard.py` (router sin lógica) → `app/services/dashboard_service.py`
  (`group_by` + `func.count`, `_visibility_clause` por rol, soft-deleted excluidos)
  → `app/schemas/dashboard.py`.

### Frontend
- `pages/DashboardStatsPage.jsx` + ruta `/dashboard` + hook `useDashboardStats`
  (`{ data, loading, error, refetch }`) + `api/dashboard.js`.
- `components/SeverityMatrixGrid.jsx`: grilla 3×3 con counts protagonistas
  («N riesgos» grande, «M issues» debajo) y el número de severidad pequeño y tenue
  en la esquina inferior izquierda (iteración pedida por el usuario).
- `components/StatusBarChart.jsx`: barras con color semántico por estado —
  abierto azul acento, en progreso ámbar, cerrado verde, derivado gris
  (iteración pedida por el usuario).
- Fuentes únicas de verdad respetadas con exports nuevos: `SEVERITY_MATRIX`
  (`utils/severityCalc.js`), `severityClass` (`SeverityBadge.jsx`) y
  `STATUS_CONFIG` con la nueva propiedad `bar` (`StatusBadge.jsx`).
- `components/AppHeader.jsx` extraído del header inline de `Dashboard.jsx`,
  con el link «Dashboard» nuevo.

## Tests
- Backend: 6 tests de integración nuevos (`test_dashboard.py`) — auth requerida,
  admin ve todo, filtrado por usuario, zero-fill, consistencia de totales.
  Suite completa: **379 passed, coverage 92%** (`dashboard_service` al 100%).
- Frontend: tests de grilla (incl. indicador de severidad en la esquina), bar chart
  (incl. color por estado), hook y biyección de la matriz.
  Suite completa: **71 passed**. Build de producción OK.
- TDD: rojo → implementación → verde en cada iteración.

## Verificación en vivo (Docker Compose + Playwright MCP)
- Login admin → `/dashboard`: matriz con counts que coinciden con el endpoint
  (8 risks visibles — el soft-deleted excluido — y 5 issues), colores correctos
  (1–3 rojo, 4–6 amarillo, 7–9 verde), charts de estado consistentes.
- `GET /api/v1/dashboard/stats` sin token → 401.
- Cada iteración visual se validó con screenshot antes de pushear.

## Resultado
Dashboard agregado con la matriz de severidad de la metodología como grilla central
y los estados como bar charts, filtrado por rol en el backend. Tres iteraciones de
UX guiadas por el usuario sobre la versión local corriendo en Docker.
