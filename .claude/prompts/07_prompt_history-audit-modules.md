# Prompt 07 — Módulos de historial y auditoría

## Contexto
Implementación de los módulos de historial de transiciones y log de auditoría, ambos append-only.

## Prompts

### Módulo history (TDD)
```
Implementá el módulo de historial de transiciones siguiendo TDD:

Entidad HistoryEntry (append-only, NUNCA se modifica ni elimina):
- id (UUID), entity_type (risk|issue), entity_id (UUID)
- from_status (nullable — primera transición no tiene from), to_status
- changed_by (UUID, nullable — FK sin constraint explícita)
- notes (texto opcional), created_at

Sin FK explícitas en entity_id para poder referenciar tanto risks como issues
desde la misma tabla (discriminator pattern).

Endpoint:
- GET /api/v1/history/{entity_type}/{entity_id} — historial paginado de una entidad

Auto-recording:
- Integrar record_transition() en risk_service y issue_service
- Se debe llamar automáticamente en cada transición de estado
- También registrar la transición al derivar un issue (in_progress → derived en el risk)

Tests requeridos (TDD):
- Crear riesgo y transicionarlo — verificar que se registran las entradas
- Derivar issue — verificar que se registra transición in_progress→derived en el riesgo
- Endpoint GET history devuelve entradas en orden cronológico inverso
```

### Módulo audit log (TDD)
```
Implementá el módulo de auditoría completo siguiendo TDD:

Entidad AuditLog (append-only, NUNCA se modifica ni elimina):
- id (UUID), user_id (nullable), action (VARCHAR 50)
- entity_type (VARCHAR 50), entity_id (UUID nullable)
- changes (JSONB), ip_address (nullable), created_at

log_action() debe llamarse en TODAS las operaciones mutantes:
- risk: create, update, delete, status_transition, derive_issue
- issue: create, update, delete, status_transition  
- project: create, update, delete
- auth: register, approve_user, deactivate_user, update_user

Endpoint (solo admin):
- GET /api/v1/admin/audit-log — log paginado con filtros: ?user_id=&action=&entity_type=&entity_id=

Tests requeridos (TDD):
- Crear riesgo → verificar que se registra en audit_log
- Transicionar estado → verificar registro
- Aprobar usuario → verificar registro
- Endpoint protegido: solo admins pueden acceder
- Filtros funcionan correctamente
```

## Branch
`feat/issues`

## Resultado
- history_service.py con record_transition()
- audit_service.py con log_action()
- Ambos integrados en todos los services
- Endpoints con paginación
