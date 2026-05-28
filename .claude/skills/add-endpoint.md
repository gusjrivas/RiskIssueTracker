# Skill: Add Endpoint

Checklist para agregar un endpoint completo siguiendo las convenciones del proyecto.

---

## Checklist en orden — TDD primero

### 0. Tests (ANTES de escribir el código)
- Crear `tests/unit/services/test_{recurso}_service.py` con los casos de uso esperados
- Crear `tests/integration/api/test_{recurso}.py` con los endpoints y sus respuestas esperadas
- Correr los tests: deben estar en **rojo** antes de implementar
- El código se escribe para hacer pasar los tests, no al revés

### 1. Schema (`app/schemas/{recurso}.py`)
- Definir `{Recurso}Create` con campos requeridos para creación
- Definir `{Recurso}Update` con todos los campos opcionales (Optional)
- Definir `{Recurso}Response` con todos los campos que devuelve la API
- Importar enums **únicamente** desde `app/schemas/common.py`
- Nunca incluir `severity` en Create/Update si se calcula automáticamente

### 2. Model (`app/models/{recurso}.py`)
- Definir clase SQLAlchemy heredando de `Base` (importar de `app/db/base`)
- Columnas: `id` UUID con `default=uuid.uuid4`, `created_at`, `updated_at` con `default=func.now()`
- FKs con `index=True` siempre
- Columnas de filtro frecuente con `index=True` (status, severity, project_id)

### 3. Service (`app/services/{recurso}_service.py`)
- Toda la lógica de negocio vive aquí — el router no toma decisiones
- Recibe `db: Session` como primer argumento
- Si el endpoint crea/modifica un Risk: llamar `get_severity()` de `severity_calculator`
- Toda operación mutante llama a `audit_service.log()` al finalizar
- Usar `db.commit()` + `db.refresh()` al final de cada escritura

### 4. Router (`app/api/{recurso}.py`)
- Solo recibe request, llama al service, devuelve response
- Todo endpoint autenticado recibe `current_user: User = Depends(get_current_user)`
- Endpoints admin-only agregan `Depends(require_admin)` además
- Prefijo y tags ya definidos en `main.py` — no redefinir en el router

### 5. Registrar en `main.py`
- `app.include_router(router, prefix=f"{settings.api_prefix}/{recurso}", tags=[...])`

### 6. Correr los tests
- `pytest tests/unit/services/test_{recurso}_service.py` → todos en verde
- `pytest tests/integration/api/test_{recurso}.py` → todos en verde
- Si alguno falla, corregir antes de continuar al paso 7

### 7. Migración (si hay tabla nueva o columna nueva)
- Correr `/new-migration` para obtener el comando correcto
- Nunca editar `init.sql` directamente — las migraciones van en `migrations/versions/`

---

## Patrón de endpoint con auth

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import get_current_user, require_admin
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[RecursoResponse])
def list_recursos(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return recurso_service.list(db, page=page, size=size)
```

## Patrón de paginación en el service

```python
def list(db: Session, page: int, size: int) -> dict:
    query = select(Model)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(query.offset((page - 1) * size).limit(size)).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size),
    }
```
