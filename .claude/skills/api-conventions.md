# Skill: API Conventions

---

## Base URL y versionado

```
http://localhost:8000/api/v1/{recurso}
```

Todos los recursos en plural. El prefijo `/api/v1` está en `settings.api_prefix`.

---

## Autenticación

Header requerido en todos los endpoints excepto `/auth/*`:

```
Authorization: Bearer {jwt_token}
```

El JWT contiene: `{ sub: user_id, role: "admin"|"user", status: "active", exp: ... }`

---

## Formato de errores

Todos los errores siguen el formato de FastAPI:

```json
{ "detail": "Mensaje descriptivo en español" }
```

Para errores de validación (422):
```json
{
  "detail": [
    { "loc": ["body", "probability"], "msg": "field required", "type": "value_error.missing" }
  ]
}
```

---

## Paginación

Query params: `?page=1&size=20` (defaults: page=1, size=20, max size=100)

Response envelope:
```json
{
  "items": [...],
  "total": 45,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

---

## Códigos HTTP por situación

| Situación | Código |
|---|---|
| GET exitoso (lista o detalle) | 200 |
| POST exitoso (creación) | 201 |
| PATCH exitoso (actualización) | 200 |
| DELETE exitoso | 204 |
| Recurso no encontrado | 404 |
| Datos inválidos | 422 |
| Sin token / token inválido | 401 |
| Sin permisos (no admin) | 403 |
| User pendiente de aprobación | 403 |
| User inactivo | 403 |
| Transición de estado inválida | 409 |
| Conflicto de unicidad | 409 |

---

## Convenciones de response

- **Fechas**: ISO 8601 con timezone (`2025-05-27T14:30:00Z`)
- **UUIDs**: string en formato estándar (`"550e8400-e29b-41d4-a716-446655440000"`)
- **Enums**: string lowercase con underscore (`"in_progress"`, `"muy_alta"`)
- **Severidad**: entero 1–9
- **Booleanos**: `true` / `false`
- **Nulos**: `null` (no omitidos)

---

## Endpoints de auth

```
POST /api/v1/auth/google      body: { id_token: string }
POST /api/v1/auth/register    body: { email, password, full_name }
POST /api/v1/auth/login       body: { email, password }
```

Response de login/register exitoso:
```json
{ "access_token": "...", "token_type": "bearer", "user": { ...UserResponse } }
```

---

## Endpoints de admin (requieren role=admin)

```
GET    /api/v1/admin/users
PATCH  /api/v1/admin/users/{id}/approve
PATCH  /api/v1/admin/users/{id}/deactivate
```

---

## Endpoints de severidad recalculada

Cuando un PATCH en Risk modifica `probability`, `impact` o `proximity`, la response incluye los valores recalculados de `exposure`, `exposure_zone` y `severity`. El cliente no envía estos campos.
