# Prompt 19 — Feature: owner assignment y activity log

## Contexto
Los riesgos e issues necesitan tener un responsable (owner) asignado. Además, se requiere un registro completo de todos los usuarios que editen cualquier campo de un riesgo o issue, con historial de cambios de owner.

## Branch
`fix/mitigation-plan-save-guard`

## Prompt
```
como punto de mejora tanto los riesgos como los problemas tienen que tener un 
responsable (owner) asignado. Estos seran usuarios dados de alta en el sistema. 
se puede cambiar el responsable de un riesgo o problema pero siempre se deberá 
llevar un log con los cambios de owner que se realicen. también se debe llevar 
un registro de cada usuario que edite, agregue o modifique cualquier campo de 
un riesgo o problema hasta que se cierren
```

## Implementación

### Backend

#### Endpoint de usuarios
```python
# GET /api/v1/users — usuarios activos para dropdowns (no requiere admin)
@router.get("", response_model=PaginatedResponse[UserBasic])
def list_users(page=1, size=100, db=Depends(get_db), current_user=Depends(get_current_user)):
    ...
```

#### Schema UserBasic
```python
class UserBasic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str
    email: str
```

#### Audit con before/after por campo
```python
# update_risk / update_issue — captura cambios campo a campo
changes = {}
for field, new_val in update_dict.items():
    old_val = getattr(risk, field)
    if str(old_val) != str(new_val):
        if field == "owner_id":
            changes["owner"] = {
                "from_id": str(old_val), "from_name": resolve_user_name(old_val),
                "to_id": str(new_val),   "to_name": resolve_user_name(new_val),
            }
        else:
            changes[field] = {"from": str(old_val), "to": str(new_val)}
    setattr(risk, field, new_val)

# Acción adicional específica para cambio de owner
if owner_change:
    log_action(action="owner_change", changes=owner_change)
```

#### Endpoint de audit por entidad
```python
# Colocado ANTES de /{risk_id} para evitar conflicto de rutas
@router.get("/{risk_id}/audit", response_model=PaginatedResponse[AuditEntryResponse])
def get_risk_audit(risk_id, ...):
    rows = db.execute(
        select(AuditLog, User.full_name.label("editor_name"))
        .outerjoin(User, AuditLog.user_id == User.id)
        .where(AuditLog.entity_type == "risk", AuditLog.entity_id == risk_id)
        .order_by(AuditLog.created_at.desc())
    ).all()
```

### Frontend

#### Componente OwnerField
- Muestra el nombre del owner actual (resuelto desde `useUsers`)
- Botón de edición → dropdown inline con todos los usuarios activos
- Save / Cancel sin navegación
- Prop `readOnly` para riesgos derivados o issues cerrados

#### Componente ActivityLog
- Consume `GET /{id}/audit`
- Acciones mapeadas a texto legible: create, update, owner_change, status_change, derive, delete, restore
- `ChangeDetail`: muestra "from → to" por campo con `FIELD_LABELS` en español
- Para `owner_change`: muestra nombres en lugar de UUIDs

#### Integración en páginas de detalle
```jsx
// RiskDetailPage y IssuesPage
<OwnerField ownerId={risk.owner_id} onSave={handleOwnerSave} readOnly={isDerived} />
<ActivityLog entityType="risk" entityId={riskId} />
```

## Resultado
- Riesgos e issues tienen campo owner_id (nullable, FK a users)
- OwnerField en páginas de detalle con edición inline
- Dropdown de owner en formularios de creación (RiskForm, IssueForm)
- Activity log muestra timeline completo con before/after por campo
- Cambios de owner registran acción `owner_change` además de `update`
- `GET /api/v1/users` disponible para todos los usuarios autenticados
