---
path: backend/**
---

# Backend Rules

## Separación de capas

- **Routers** (`app/api/`): solo reciben requests HTTP y devuelven responses. Sin lógica de negocio. Delegan todo al service correspondiente.
- **Services** (`app/services/`): toda la lógica de negocio vive aquí. Son llamados por los routers y llaman a los modelos/DB.
- **Models** (`app/models/`): solo definen la estructura de las tablas SQLAlchemy. Sin métodos de negocio.
- **Schemas** (`app/schemas/`): solo validación y serialización Pydantic. Sin acceso a DB.

## Naming

- Archivos en `snake_case` (ej. `risk_service.py`, `mitigation_plan.py`)
- Clases en `PascalCase` (ej. `RiskService`, `MitigationPlan`)
- Rutas HTTP: `/api/v1/{recurso}` siempre en plural (ej. `/api/v1/risks`, `/api/v1/projects`)

## Patrones obligatorios

- Todo endpoint recibe `db: Session = Depends(get_db)` — nunca crear sessions manualmente.
- Los enums del dominio (RiskStatus, IssueStatus, Severity, etc.) se definen **únicamente** en `app/schemas/common.py` y se importan desde ahí.
- La lógica de cálculo de severidad se implementa **únicamente** en `app/services/severity_calculator.py`. Ningún otro módulo debe replicar esa fórmula.
- Los schemas de request y response se definen en `app/schemas/{recurso}.py` con sufijos `Create`, `Update`, `Response`.
