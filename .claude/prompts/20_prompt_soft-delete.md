# Prompt 20 — Feature: soft delete (borrado lógico)

## Contexto
Los borrados de riesgos e issues deben ser lógicos (soft delete), no físicos. El usuario administrador puede restaurar un riesgo o issue dado de baja.

## Branch
`fix/mitigation-plan-save-guard`

## Prompt
```
todos los borrados de los riesgos o problemas seran borrados lógicos. El usuario 
administrador tendrá la funcionalidad de volver activar un riesgo o isue dado de baja
```

## Implementación

### Migración Alembic
```python
# 9dcf00d01c37_soft_delete_risks_and_issues.py
def upgrade():
    op.add_column('risks',  sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_risks_deleted_at',  'risks',  ['deleted_at'])
    op.add_column('issues', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_issues_deleted_at', 'issues', ['deleted_at'])
```

### Modelos
```python
deleted_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), nullable=True, default=None, index=True
)
```

### Servicios — filtro en lecturas
```python
# get_risk: excluye eliminados
select(Risk).where(Risk.id == risk_id, Risk.deleted_at.is_(None))

# list_risks: excluye eliminados
select(Risk).where(Risk.deleted_at.is_(None))
```

### Servicios — soft delete en lugar de hard delete
```python
def delete_risk(db, risk_id, current_user):
    risk = get_risk(db, risk_id)
    _assert_can_modify(risk, current_user)
    risk.deleted_at = datetime.now(timezone.utc)   # soft delete
    db.commit()
    log_action(action="delete", ...)

def restore_risk(db, risk_id, current_user):
    if current_user.role != UserRole.admin:
        raise HTTPException(403, "Solo administradores pueden restaurar riesgos")
    risk = db.execute(select(Risk).where(Risk.id == risk_id)).scalar_one_or_none()
    risk.deleted_at = None
    db.commit()
    log_action(action="restore", ...)

def list_deleted_risks(db, page, size):
    return select(Risk).where(Risk.deleted_at.is_not(None))
```

### Endpoints
```python
# PATCH /api/v1/risks/{id}/restore  (admin check en servicio)
# PATCH /api/v1/issues/{id}/restore

# GET /api/v1/admin/deleted-risks   (require_admin)
# GET /api/v1/admin/deleted-issues  (require_admin)
```

### Frontend — Papelera en AdminPage
- Sección "Papelera" con contador en rojo si hay elementos eliminados
- Lista separada de riesgos eliminados e issues eliminados
- Muestra: tipo, severidad badge, título, fecha de eliminación
- Botón "Restaurar" por fila → llama a `PATCH /{id}/restore` → elimina la fila localmente
- Carga en paralelo con `Promise.all([getDeletedRisks(), getDeletedIssues()])`

```jsx
function TrashRow({ item, type, onRestore }) {
  return (
    <div className="card flex items-center justify-between">
      <div>
        <SeverityBadge severity={item.severity} />
        <p>{item.title}</p>
        <p>Eliminado: {format(item.deleted_at)}</p>
      </div>
      <button onClick={onRestore}>
        <RotateCcw /> Restaurar
      </button>
    </div>
  )
}
```

## Resultado
- Eliminar un riesgo/issue lo mueve a la papelera (deleted_at = now) en lugar de borrarlo físicamente
- Las listas y el detalle excluyen registros con deleted_at
- El audit log registra acción `delete` y `restore`
- AdminPage tiene sección Papelera visible solo para admins
- Admin puede restaurar cualquier riesgo o issue eliminado con un clic
