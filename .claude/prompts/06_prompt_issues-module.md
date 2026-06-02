# Prompt 06 — Módulo de issues

## Contexto
Implementación del módulo de issues con creación manual y derivación desde riesgos.

## Prompts

### Módulo issues (TDD)
```
Implementá el módulo de issues siguiendo TDD:

Entidad Issue:
- id (UUID), project_id (FK, NOT NULL), risk_id (FK nullable — si fue derivado de un riesgo)
- title, description (opcional), severity (entero 1-9)
- status (issue_status: open|in_progress|closed), default open
- mitigation_strategy, contingency_plan
- owner_id (FK users, nullable), created_by (FK users, NOT NULL)
- created_at, updated_at

Endpoints (todos requieren autenticación):
- GET /api/v1/issues — listar con filtros: ?project_id=&status=&risk_id=&page=&size=
- POST /api/v1/issues — crear issue manualmente
- POST /api/v1/issues/derive — derivar desde un riesgo {"risk_id": "..."}
- GET /api/v1/issues/{id} — detalle
- PATCH /api/v1/issues/{id} — actualizar
- PATCH /api/v1/issues/{id}/status — transición de estado
- DELETE /api/v1/issues/{id} — eliminar

Flujo de derivación (POST /issues/derive):
1. Verificar que el riesgo existe y está en estado in_progress
2. Crear Issue con mismos title, description, severity que el Risk
3. Actualizar Risk: status=derived, derived_issue_id=issue.id
4. Retornar el Issue creado

Máquina de estados Issue:
- open → in_progress
- in_progress → closed
- Cualquier otra → 400

Tests requeridos (TDD):
- Derivar issue desde riesgo en_progreso
- Error al derivar desde riesgo en estado incorrecto
- Error al derivar si el riesgo ya tiene issue derivado
- CRUD completo con ownership
- Transiciones válidas e inválidas
```

## Branch
`feat/issues`

## Resultado
- issue_service.py con lógica de derivación
- Relación bidireccional Risk ↔ Issue (derived_issue_id / risk_id)
- FK circular resuelta con ALTER TABLE diferido en init.sql
</content>
</invoke>