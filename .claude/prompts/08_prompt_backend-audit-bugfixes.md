# Prompt 08 — Auditoría del backend y corrección de bugs

## Contexto
Antes de avanzar con el frontend, revisión exhaustiva del backend para detectar y corregir todos los bugs existentes.

## Prompts

### Auditoría completa del backend
```
antes de avanzar con el frontend veridiquemos nuevamente todo el backend construido y que no haya bugs
```

### Bugs encontrados y corregidos

Durante la auditoría se detectaron 5 bugs:

1. **Type annotations incorrectas en modelos SQLAlchemy**
   - `Mapped[str]` en columnas `DateTime` → corregido a `Mapped[datetime]`
   - Afectaba: User, Project, Risk, Issue, HistoryEntry, AuditLog models

2. **FK cascade faltante**
   - `derived_issue_id` en Risk no tenía `ondelete="SET NULL"`
   - `changed_by` en HistoryEntry tampoco

3. **record_transition no se llamaba al derivar un issue**
   - `issue_service.derive_from_risk()` no registraba la transición `in_progress → derived` en el risk

4. **log_action no se llamaba en endpoints admin**
   - `approve_user` y `deactivate_user` en admin.py no registraban la acción

5. **Tests de unidad con assert_called_once() muy estrictos**
   - `db.add.assert_called_once()` fallaba porque `log_action` llama `db.add` adicionales veces
   - Corregido a `assert db.add.call_count >= 1`

### Corrección de tests que fallaban por audit log
```
los 6 test que fallaron en el backend son por el tema del audit log cuando hacemos add y commit 
en el service. revisá y arreglá
```

## Branch
`feat/issues`

## Resultado
- 342 tests pasando sin fallas
- Todos los modelos con tipos correctos
- Cascadas FK correctas
- Auditoría y historial completos en todos los flujos
