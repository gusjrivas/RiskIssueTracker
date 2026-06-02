# Prompt 05 — Módulo de riesgos

## Contexto
Implementación del módulo de riesgos con cálculo automático de severidad y máquina de estados.

## Prompts

### Módulo risks (TDD)
```
Implementá el módulo de riesgos siguiendo TDD:

Entidad Risk:
- id (UUID), project_id (FK, NOT NULL), title, description (opcional)
- category (risk_category enum), probability, impact, proximity
- severity (entero 1-9, calculado automáticamente)
- status (risk_status: open|in_progress|closed|derived), default open
- mitigation_strategy (texto), contingency_plan (texto)
- owner_id (FK users, nullable), created_by (FK users, NOT NULL)
- derived_issue_id (FK issues, nullable — FK circular diferida)
- created_at, updated_at

Endpoints (todos requieren autenticación):
- GET /api/v1/risks — listar con filtros: ?project_id=&status=&category=&page=&size=
- POST /api/v1/risks — crear (severidad calculada automáticamente con severity_calculator)
- GET /api/v1/risks/{id} — detalle
- PATCH /api/v1/risks/{id} — actualizar (recalcular severidad si cambia prob/impact/proximity)
- PATCH /api/v1/risks/{id}/status — transición de estado con validación de la máquina de estados
- DELETE /api/v1/risks/{id} — eliminar

Máquina de estados:
- open → in_progress
- in_progress → closed (mitigado)
- in_progress → derived (se crea Issue vinculado)
- Cualquier otra transición → 400

Ownership: solo creador u owner o admin puede modificar/transicionar

Tests requeridos (TDD):
- Crear riesgo calcula severidad correctamente (varios casos de la matriz)
- Transiciones válidas e inválidas
- Filtros de lista funcionan
- Ownership check
- Recálculo de severidad al actualizar
```

## Branch
`feat/risks`

## Resultado
- Tests de risks pasando (acumulado con módulos anteriores)
- risk_service.py con severidad automática
- Validación de máquina de estados en cada transición
- RiskCreate, RiskUpdate, RiskResponse, RiskStatusUpdate schemas
