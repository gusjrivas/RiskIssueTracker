# Skill: Backend Best Practices

---

## SQLAlchemy 2.0

Usar siempre la nueva sintaxis con `select()`:

```python
# Correcto
from sqlalchemy import select, func
stmt = select(Risk).where(Risk.project_id == project_id).order_by(Risk.severity)
risks = db.scalars(stmt).all()

# Incorrecto — no usar Query API legacy
db.query(Risk).filter(...)
```

Para escalares únicos:
```python
risk = db.scalar(select(Risk).where(Risk.id == risk_id))
if risk is None:
    raise HTTPException(status_code=404, detail="Risk not found")
```

---

## Pydantic v2

```python
# model_validator para validaciones cruzadas
from pydantic import model_validator

class RiskCreate(BaseModel):
    @model_validator(mode="after")
    def validate_fields(self):
        # validaciones aquí
        return self

# field_validator para un campo
from pydantic import field_validator

@field_validator("probability")
@classmethod
def check_probability(cls, v):
    return v
```

Los modelos SQLAlchemy se convierten a schema con `model_validate`:
```python
RiskResponse.model_validate(risk_orm)  # requiere model_config = ConfigDict(from_attributes=True)
```

---

## Auth JWT

### Dependencias reutilizables

```python
# get_current_user → lanza 401 si token inválido o user inactive/pending
# require_admin   → lanza 403 si el user no es admin
```

Siempre usar `Depends(get_current_user)` en endpoints autenticados.
Agregar `Depends(require_admin)` solo en endpoints de administración.

### Google OAuth flow

1. Frontend recibe `id_token` de Google
2. `POST /auth/google` con `{id_token: string}`
3. Backend verifica con `google.oauth2.id_token.verify_oauth2_token()`
4. Extrae `email`, `name`, `picture`, `sub` (google_id)
5. Busca user por `google_id` o `email`, crea si no existe con `status=pending`
6. Si `status != active` → 403
7. Devuelve JWT propio

### Email/Password flow

1. `POST /auth/register` → crea user con `password_hash`, `status=pending`
2. `POST /auth/login` → verifica hash con `passlib`, devuelve JWT si `status=active`

---

## Transacciones

Para operaciones que tocan múltiples tablas (como `derive_to_issue`):

```python
try:
    # todas las operaciones
    db.add(issue)
    db.flush()          # asigna ID sin commitear
    risk.status = RiskStatus.derived
    risk.derived_issue_id = issue.id
    audit_service.log(...)
    db.commit()
    db.refresh(issue)
    return issue
except Exception:
    db.rollback()
    raise
```

---

## Errores HTTP estándar

| Situación | Código |
|---|---|
| Recurso no encontrado | 404 |
| Validación de datos | 422 (automático con Pydantic) |
| Sin autenticación | 401 |
| Sin permisos | 403 |
| Conflicto de estado (ej: derivar risk ya closed) | 409 |
| Error de servidor | 500 |

```python
raise HTTPException(status_code=409, detail="Risk already derived or closed")
```

---

## TDD — regla de desarrollo

Todo código nuevo requiere tests. El flujo obligatorio es:

1. Escribir el test que describe el comportamiento → **rojo**
2. Implementar el mínimo código para pasar → **verde**
3. Refactorizar manteniendo verde

```bash
# Correr tests durante el desarrollo
pytest tests/unit/services/test_mi_service.py -v

# Con coverage antes de commitear
pytest --cov=app --cov-report=term-missing tests/
```

Ver patrones detallados en el skill [testing.md](testing.md).

---

## AuditService

Llamar al final de toda operación mutante en los services:

```python
audit_service.log(
    db=db,
    user_id=current_user.id,
    action="create",           # create | update | delete | status_change | derive | approve | deactivate | login
    entity_type="risk",
    entity_id=risk.id,
    changes={"title": {"before": None, "after": risk.title}},
)
```
