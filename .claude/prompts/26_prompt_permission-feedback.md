# Prompt 26 — Fix: informar restricción de permisos en riesgos e issues

## Contexto
El backend ya restringía modificar/transicionar/eliminar/derivar a creador, responsable
o admin (403), pero el frontend mostraba todas las acciones activas para cualquier usuario
y se tragaba los errores: un usuario sin permiso hacía click y la acción fallaba en
silencio, sin ninguna indicación.

## Branch
`fix/permission-feedback` → PR #41

## Prompts

```
encontré un bug importante los riesgos y problemas pueden ser modificados editados o
cambiados de estados solo por el usuario o bien que los creo o bien por el usuario que
tiene asignado el riesgo o en ultima instancia un user admin puede hcaer cualquier
cambio. Actualmente cuando un usario que no es pripietario del riesgo o problema o no
lo creo le deja hacer las acciones pero no se indica en ningun momento que el usuario
no lo puede hacer, en estos casos siempre se debe informar al usuario esa restricción
o no esta clara
```

UX elegida (entre ocultar acciones / deshabilitarlas con mensaje / solo error al intentar):
**botones visibles pero deshabilitados + banner explicativo**.

## Implementación (solo frontend)

### Nuevo util `frontend/src/utils/permissions.js`
```js
export function canModifyEntity(user, entity) {
  if (!user || !entity) return false
  return user.role === 'admin' || entity.created_by === user.id || entity.owner_id === user.id
}
```
Refleja la regla del backend (`risk_service` / `issue_service`).

### `RiskDetailPage.jsx` / `IssuesPage.jsx`
- Banner cuando `!canModify`: *«Solo el creador, el responsable asignado o un
  administrador pueden modificar este riesgo/issue o cambiar su estado.»*
- `disabled={!canModify}` en: transición de estado, derivar a issue, eliminar,
  cambiar responsable y plan de mitigación — todos con tooltip explicativo.
- `try/catch` en `handleDerive`/`handleDelete` → error visible junto a las acciones.

### `StatusTransitionButton.jsx` / `OwnerField.jsx`
- Nuevo prop `disabled` (botón grisado con `title`).
- Manejo de errores como respaldo: si el backend rechaza igual una acción, el mensaje
  (ej. *«Sin permiso para cambiar el estado de este riesgo»*) se muestra en pantalla
  en vez de perderse.

### `MitigationPlanPanel.jsx`
- Nuevo prop `disabled`: textareas en solo lectura + botón «Guardar plan» deshabilitado
  (distinto de `readOnly`, que se mantiene para derived/closed).

## Tests
- Frontend: **56 passed** (17 nuevos: `permissions.test.js`,
  `StatusTransitionButton.test.jsx`, `OwnerField.test.jsx`)
- TDD: rojo → implementación → verde.

## Verificación en vivo (Docker Compose + Playwright MCP)
- Usuario ajeno abre un riesgo creado por admin → banner visible; eliminar, responsable,
  «Iniciar» y «Guardar plan» todos `[disabled]`
  (screenshot `test-screenshots/fix-permisos-usuario-sin-permiso.png`).
- Admin abre el mismo riesgo → sin banner, todo habilitado.

## Resultado
El usuario siempre sabe que no puede operar sobre un riesgo/issue ajeno: lo ve antes de
intentar (banner + controles grisados) y, si algo igual falla contra el backend, el
mensaje de error se muestra en pantalla.
