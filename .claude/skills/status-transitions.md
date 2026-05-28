# Skill: Status Transitions

Toda transición de estado debe: validar que sea válida, persistir el nuevo estado, insertar en `history_entries`, y llamar a `audit_service.log()`.

---

## Risk — máquina de estados

```
open ──────────────→ in_progress ──────────→ closed   (mitigado)
                          │
                          └─────────────────→ derived  (se materializó → Issue abierto)
```

### Transiciones válidas

| Desde | Hacia | Condición |
|---|---|---|
| `open` | `in_progress` | Ninguna |
| `in_progress` | `closed` | Ninguna |
| `in_progress` | `derived` | Solo desde `in_progress` |

Cualquier otra transición → HTTP 409.

### Flujo completo `in_progress → derived`

Operación atómica en `risk_service.derive_to_issue(risk_id, db, current_user)`:

```
1. Verificar risk.status == in_progress  (sino → 409)
2. Crear Issue con:
   - title          = risk.title
   - description    = risk.description
   - severity       = risk.severity   (hereda)
   - project_id     = risk.project_id
   - risk_id        = risk.id
   - owner_id       = risk.owner_id
   - status         = open
   - contingency_plan = risk.contingency_plan
3. db.flush()  → obtener issue.id
4. Actualizar Risk:
   - status          = derived
   - derived_issue_id = issue.id
5. INSERT history_entries:
   - entity_type = risk, entity_id = risk.id
   - from_status = in_progress, to_status = derived
   - notes = f"Derivado a Issue {issue.id}"
6. INSERT history_entries:
   - entity_type = issue, entity_id = issue.id
   - from_status = null, to_status = open
7. audit_service.log(action="derive", entity_type="risk", entity_id=risk.id, ...)
8. db.commit()
```

---

## Issue — máquina de estados

```
open ──────────────→ in_progress ──────────→ closed
```

### Transiciones válidas

| Desde | Hacia |
|---|---|
| `open` | `in_progress` |
| `in_progress` | `closed` |

---

## Implementación de cualquier transición de estado

```python
def transition_status(entity, new_status, valid_transitions, db, current_user, notes=None):
    if new_status not in valid_transitions.get(entity.status, []):
        raise HTTPException(status_code=409, detail=f"Invalid transition: {entity.status} → {new_status}")

    old_status = entity.status
    entity.status = new_status

    db.add(HistoryEntry(
        entity_type=entity_type,
        entity_id=entity.id,
        from_status=old_status,
        to_status=new_status,
        changed_by=str(current_user.id),
        notes=notes,
    ))

    audit_service.log(
        db=db, user_id=current_user.id,
        action="status_change", entity_type=entity_type, entity_id=entity.id,
        changes={"status": {"before": old_status, "after": new_status}},
    )
```

---

## Reglas invariantes

- Nunca transicionar un Risk en estado `closed` o `derived`
- Nunca transicionar un Issue en estado `closed`
- Todo cambio de estado genera un `HistoryEntry` (append-only)
- Todo cambio de estado genera un registro en `audit_log`
- La severidad **no** se recalcula en transiciones de estado — solo cuando cambian los campos de cálculo
