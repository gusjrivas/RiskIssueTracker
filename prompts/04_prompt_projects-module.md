# Prompt 04 — Módulo de proyectos

## Contexto
Implementación del módulo de proyectos con CRUD completo y control de ownership.

## Prompts

### Módulo projects (TDD)
```
Implementá el módulo de proyectos siguiendo TDD:

Entidad Project:
- id (UUID), name, description (opcional), client (opcional)
- created_by (FK a users, NOT NULL) — el usuario que lo creó
- created_at, updated_at (TIMESTAMPTZ)

Endpoints (todos requieren autenticación):
- GET /api/v1/projects — listar proyectos con paginación ?page=1&size=20
- POST /api/v1/projects — crear proyecto (created_by = usuario autenticado)
- GET /api/v1/projects/{id} — detalle
- PATCH /api/v1/projects/{id} — actualizar (solo el creador o admin)
- DELETE /api/v1/projects/{id} — eliminar (solo el creador o admin)

Regla de ownership:
- Solo el creador del proyecto o un admin puede modificarlo/eliminarlo
- Los demás usuarios pueden verlo

Schema ProjectUpdate: todos los campos opcionales (name, description, client)

Tests requeridos (TDD):
- CRUD completo con autenticación
- Intentar modificar proyecto ajeno → 403
- Admin puede modificar cualquier proyecto
- Paginación correcta
```

## Branch
`feat/project-setup-complete` → luego `feat/risks`

## Resultado
- 127 tests pasando
- Módulo projects con ownership check
- ProjectCreate, ProjectUpdate, ProjectResponse schemas
- project_service.py con lógica de negocio
