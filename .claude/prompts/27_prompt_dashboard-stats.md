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

---

# Iteración 2 — Bandeja única de severidad (reemplaza el flip por celda)

## Contexto
La matriz de severidad del dashboard solo mostraba counts, sin acceso directo a los
riesgos/issues de cada celda. Se pidió primero un drill-down con flip 3D por celda
(PR #48); una vez probado en local, el usuario lo consideró poco usable (celdas muy
chicas para listas, mal en mobile) y se rediseñó como una única bandeja debajo de
toda la matriz, manteniendo la misma visibilidad por rol.

## Branch
`feature/dashboard-severity-drilldown` → PR #48 (abierto con el flip por celda y
luego actualizado con la bandeja, sobre el mismo branch/PR)

## Prompts

### Primera mejora — flip por celda (PR #48)

```
vamos a incorporar una nueva funcionalidad que vincule lo que se en el dashboard de
riesgos y problemas para que cuando se presione la card se de vuelta y nos de un link
a cada riesgo o problema y que al presionr el link nos lleve directo a la pagina del
detalle de ese riesgo o problema. Esto será encarado desde una perspectiva de mejora
y vas a tener en cuenta todos los lineamientos de desarrollo back front y de diseño
marcados en este proyecto. Los links que muestres para acceder tienen que seguir la
lógica de permisos que sigue la aplicación el admin puede acceder a todo y el resto
de user pueden acceder a ver sus propios riesgos o problemas o a cuales les haya sido
asignados
```

```
cuando haga click sobre alguna card se dara vuelta y mostrará un listado de link con
una descripción mínima del riesgo o problema con link de acceso directo luego a la
url de la página donde se encuentra
```

```
esta ok podemos pasar a la implementacion
```

### Segunda mejora — bandeja única (rediseño sobre el mismo branch)

```
no es user frendly la implementación. Vamos a realizar la siguiente mejora. 1 cuando
se toque una card del dashboard toda la zona del dashboard se debe comvertir en una
bandeja donde se vean los riesgos y problemas en una lista de links ( como si fuera
una bandeja) agrupados por severidad ( es decir los de mayor severidad 1 al principio
y los mas bajos 9 al final). El componente tiene que poder visualizarse bien en un
movil. Mantener el tema de que cada usuario pueda ver sus riesgos y problemas de
acuerdo a sus permisos, salvo el admin que puede ver todo. Todo este desarrollo
mantengamoslo en el actual branch dashboard-severity-drilldown
```

```
mostrame algunas opciones de diseño antes de avanzar con la implementación
```

```
la opcion A me parece la mejor solo que hay que incorporar que se oculta la bandeja
al volver hacer click en la matriz. es decir que el usuario tenga la opcion de
desplegar la bandeja para luego presionar un link de la lista para ir directo a la
página del riesgo o problema
```

```
no termino de entender visualmente que se eliminaría
```

```
ahora comprendí, si, eliminemos el código viejo que no hace sentido el que se tenía
que voltear cada card
```

```
revisálo con los lineamientos de desarrollo de backend y frontend que estan definidos
si cumples esos lineamientos + TDD deberías estar OK, revisalo antes de codificar
```

```
si, otra cosa que debemos hacer al finalizar es actualizar el prompt 27. incorporemos
las lineas que se pidieron agregar a partir de esta ultima mejora, es decir mantener
el prompt original que se pedía por la construcción del dashboard y añadir a este
prompt la mejora que acabamos de realizar
```

```
esta Ok para avanzar con la implementacion
```

## Decisiones de diseño (brainstorming + plan aprobados)

- **Opción A** (de tres mockups visuales: panel debajo de la matriz, bandeja
  reemplazando la matriz, bottom sheet/overlay): la matriz 3×3 queda siempre visible
  arriba; debajo se despliega una bandeja full-width.
- **Toggle único**: cualquiera de las 9 celdas abre/cierra la misma bandeja
  (`if (!open) onOpenDrawer(); setOpen(o => !o)`), sin resaltar ni hacer scroll hacia
  la severidad clickeada — la bandeja siempre muestra el listado completo.
- **Una sola llamada agrupada**: nuevo endpoint `GET /stats/severity-items` devuelve
  todas las severidades 1–9 con items visibles (sin las que no tienen), cada grupo con
  riesgos primero y luego issues, ambos ordenados por título — reemplaza el endpoint
  por severidad+tipo del flip (`GET /stats/severity/{severity}?type=`).
- **Visibilidad sin cambios**: se reutiliza `_visibility_clause` (admin ve todo, user
  regular solo owner/creador/proyecto propio), igual que `/dashboard/stats`.
- **Mobile-first**: bandeja en stack vertical, `flex-wrap` por item, sin `max-h`/scroll
  interno — sección normal de la página.
- Se elimina por completo el código del flip 3D (PR #48) al quedar sin uso.

## Implementación

### Backend
- `GET /api/v1/dashboard/stats/severity-items` → `{ groups: [{ severity, items: [{id, title, status, type}] }] }`,
  `groups` ordenado 1→9, solo severidades con items, `risk` antes que `issue` dentro
  de cada grupo, ambos ordenados por `title`. Excluye soft-deleted.
- `app/services/dashboard_service.get_severity_items_grouped` (reutiliza
  `_visibility_clause`) → `app/schemas/dashboard.py` (`SeverityGroupItem`,
  `SeverityGroup`, `SeverityItemsGroupedResponse`).
- Eliminado: endpoint `GET /stats/severity/{severity}?type=`, schemas `SeverityItem`/
  `SeverityItemsResponse`, service `get_severity_items`.

### Frontend
- `api/dashboard.js`: `getSeverityGroups` (reemplaza `getSeverityItems`).
- `hooks/useSeverityGroups.js`: fetch lazy on-demand (`fetchGroups`), con cache y
  reintento tras error.
- `components/SeverityDrawer.jsx` (nuevo): bandeja presentacional — agrupa por
  severidad con `SeverityBadge`, cada item es un `<Link>` a `/risks/{id}` o
  `/issues/{id}` con etiqueta de tipo, título truncado y `StatusBadge`.
- `components/SeverityMatrixGrid.jsx`: vuelve a celdas simples con
  `aria-expanded`/`aria-controls="severity-drawer"`, estado `open` local, renderiza
  `<SeverityDrawer>` debajo de la grilla 3×3.
- `pages/DashboardStatsPage.jsx`: usa `useSeverityGroups`, pasa `groups`,
  `groupsLoading`, `groupsError`, `onOpenDrawer={fetchGroups}`.
- Eliminado: `SeverityCellFlip.jsx`, `useSeverityItems.js` y sus tests.

## Tests
- Backend: nueva clase `TestSeverityItemsGrouped` (6 tests) reemplaza
  `TestSeverityItems`. Suite completa: **385 passed**.
- Frontend: nuevos tests de `useSeverityGroups` (4), `SeverityDrawer` (5) y
  `SeverityMatrixGrid` reescrito (8). Suite completa: **82 passed** (12 archivos).
- TDD en cada tarea (subagent-driven-development: implementación → spec review →
  code quality review).

## Verificación en vivo (Docker Compose + Playwright MCP)
- Login admin → `/dashboard`: click en cualquiera de las 9 celdas abre la bandeja
  con los grupos de severidad presentes en los datos seedeados (1, 3, 5, 7), riesgos
  e issues mezclados con `StatusBadge` correcto.
- Click en un link de tipo Riesgo → navega a `/risks/{id}`; click en un link de tipo
  Issue → navega a `/issues/{id}`.
- Click en una celda distinta con la bandeja abierta → la oculta (toggle), sin
  re-disparar el fetch.
- Viewport mobile (375×812): la matriz se apila arriba y la bandeja debajo, los items
  usan `flex-wrap` (título truncado + badge de estado en línea siguiente si no entra),
  sin overflow horizontal. Toggle de apertura/cierre verificado también en mobile.
- 0 errores de consola en todas las navegaciones.

## Resultado
El flip 3D por celda (PR #48) fue reemplazado por una bandeja única debajo de la
matriz de severidad: misma lógica de permisos, una sola llamada agrupada al backend,
y una UX mobile-friendly validada por el usuario sobre la versión local. Todo el
código del flip (`SeverityCellFlip.jsx`, `useSeverityItems.js`, endpoint y schemas
por severidad+tipo) fue eliminado al quedar sin uso.
