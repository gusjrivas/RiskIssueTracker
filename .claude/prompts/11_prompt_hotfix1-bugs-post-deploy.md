# Prompt 11 — Hotfix 1: bugs encontrados en testing local

## Contexto
Bugs detectados al probar la aplicación por primera vez en el navegador después del despliegue local.

## Branch
`hotfix/bugs-mitigation-register`

## Prompts

### Bug 1 — "Method Not Allowed" al guardar plan de mitigación
```
hay varios bugs que encontré 1 en la UI de riesgo cuando quiero guardar un plan 
con el botón guardar plan aparece un mensaje method not alowed.
```

**Causa:** El frontend siempre usó `PATCH` para actualizaciones parciales, pero los 3 routers del backend tenían `PUT`.

**Fix aplicado:**
```python
# En risks.py, issues.py, projects.py:
# Antes:
@router.put("/{id}", response_model=...)
# Después:
@router.patch("/{id}", response_model=...)
```
Tests de integración actualizados de `client.put(...)` a `client.patch(...)`.

### Bug 2 — No se podía registrar un nuevo usuario
```
otro bug que encontre es que no me permite crear o bien registrar un nuevo usuario
```

**Causa:** El mismo error UUID (`native_uuid=False`) causaba 500 en el endpoint de registro al intentar serializar el usuario creado.

**Fix:** Ya resuelto con el cambio `native_uuid=True` en todos los modelos.

### Panel de administración para aprobar usuarios
```
otro bug que encontré es que al entrar como admin no veo la opcion 
para aprobar los usarios registrados
```

**Implementado:**
- `frontend/src/pages/AdminPage.jsx` — lista usuarios con badges, botones aprobar/desactivar
- `frontend/src/api/admin.js` — `getUsers`, `approveUser`, `deactivateUser`
- `frontend/src/hooks/useAdmin.js` — estado + mutaciones
- Dashboard: link "Administración" visible solo para `role=admin`
- `ProtectedRoute`: prop `adminOnly` para proteger `/admin`

### Mensajes de error en español
```
otro bug que encontré es que todos los mensajes estan en ingles deben estar en español
```

**Fix:** Todos los `detail=` de `HTTPException` traducidos en:
- `auth_service.py`: "Token inválido", "El email ya está registrado", "No autenticado", etc.
- `api/auth.py`: "Cuenta pendiente de aprobación", "Credenciales inválidas"
- `api/admin.py`: "Usuario no encontrado"
- `risk_service.py`: "Riesgo no encontrado", "Sin permiso para modificar"
- `issue_service.py`: "Issue no encontrado", mensajes de transición
- `project_service.py`: "Proyecto no encontrado"

## Resultado
- 342 tests pasando
- Panel admin funcional
- Todos los mensajes de error en español
