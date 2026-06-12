# Prompt 25 — Fix: barrido de bugs (severidad, auth, derive, paginación)

## Contexto
Revisión completa del proyecto en busca de bugs, por mínimos que fueran. Se encontraron
y corrigieron 6, todos con TDD (test rojo → fix → verde) y verificación en vivo con la
app corriendo (Docker Compose + Playwright MCP).

## Branch
`fix/bug-sweep` → PR #39 y #40 (mergeados)

## Prompts

```
revisá todo el proyecto y buscá bugs por mas minimos que sean fixealos y todos los
fixes debes suirlos a un nuevo branch para que apruebe el PR manualmente y luego yo
decida si mergearlo o no
```

```
/run   (verificación en vivo de los fixes con la app levantada)
```

## Bugs encontrados y corregidos

### 1. Preview de severidad incorrecto — `frontend/src/utils/severityCalc.js`
Los pesos de **probabilidad** e **impacto** estaban intercambiados respecto a la fórmula
canónica (`backend/app/services/severity_calculator.py`). Ejemplo real: prob `muy_alta` ×
imp `bajo` → el preview mostraba **2 — Crítico** pero el backend guardaba **5 — Moderado**.

### 2. Error de punto flotante en la zona de exposición — `severityCalc.js`
El backend redondea la exposición a 4 decimales **antes** de clasificar la zona; el
frontend usaba el float crudo: `0.90 × 0.10 = 0.09000000000000001` caía en zona *medio*
en vez de *bajo*. Fix: `+(pw * iw).toFixed(4)` antes de zonificar.

### 3. Login fallido sin mensaje — `frontend/src/api/client.js`
Un 401 en `/auth/login` disparaba el redirect global a `/login` y devolvía `undefined`:
la página recargaba sin mostrar «Credenciales inválidas» y rompía con TypeError.
Fix: los endpoints de ingreso (`login`/`google`/`register`) propagan el error;
el redirect automático se mantiene para el resto de los endpoints.

### 4. Usuarios desactivados seguían operando la API — `backend/app/services/auth_service.py`
`get_current_user` no validaba `user.status`: un usuario desactivado por un admin mantenía
acceso total hasta que expirara su token (24 h). Fix: **403** si la cuenta no está activa.
Verificado en vivo: el mismo token pasa de 200 a 403 al desactivar la cuenta.

### 5. Derive sin permisos y sobre riesgos eliminados — `backend/app/services/issue_service.py`
`derive_from_risk` no aplicaba el chequeo creator/owner/admin que sí tienen las demás
transiciones (cualquier usuario podía derivar riesgos ajenos) y no filtraba `deleted_at`
(se podía derivar un riesgo soft-deleted). Fix: 403 y 404 respectivamente.

### 6. OFFSET negativo en paginación — `backend/app/api/admin.py`, `projects.py`
`list_users` y `list_projects` aceptaban `page=0` o `size=-1` sin validación →
OFFSET negativo → 500 en Postgres. Fix: `Query(ge=1)` / `Query(ge=1, le=100)` → 422.

## Tests
- Backend: **373 passed** (9 nuevos en `test_auth.py`, `test_issues.py`, `test_admin.py`, `test_projects.py`)
- Frontend: **39 passed** (24 nuevos: `severityCalc.test.js`, `client.test.js`)

## Resultado
- Preview y severidad guardada coinciden exactamente (verificado en vivo: ambos 5 — Moderado).
- El login fallido muestra «Credenciales inválidas» en pantalla.
- La baja lógica de usuarios surte efecto inmediato sobre tokens vigentes.
- Derive respeta permisos y soft-delete; la paginación inválida devuelve 422.
