# /audit-layers

Escanea el código y reporta violaciones de separación de capas.

## Uso

```
/audit-layers
```

---

## Qué detecta

### Backend

**Violaciones en Routers** (`app/api/*.py`):
- Imports de `sqlalchemy` directamente en routers (debería ir en services)
- Llamadas a `db.add()`, `db.commit()`, `db.query()` dentro de funciones del router
- Lógica condicional de negocio (cálculos, validaciones de dominio)
- Imports desde `app/models/` directamente en routers

**Violaciones en Schemas** (`app/schemas/*.py`):
- Imports de `sqlalchemy` o `app/db/`
- Lógica que accede a la base de datos

**Violaciones en Models** (`app/models/*.py`):
- Métodos con lógica de negocio (que no sean propiedades simples)
- Imports de services o schemas

**Violaciones de enums** (`app/**/*.py`):
- Definición de enums fuera de `app/schemas/common.py`
- Strings hardcodeados donde debería usarse un enum

**Violaciones de severidad**:
- Fórmulas de cálculo de exposición/severidad fuera de `severity_calculator.py`

### Frontend

**Violaciones en Pages** (`src/pages/*.jsx`):
- Llamadas directas a `fetch()` o `apiGet/apiPost` (deberían ir en hooks)
- Imports desde `src/api/` directamente en páginas

**Violaciones en Components** (`src/components/*.jsx`):
- Llamadas directas a `fetch()` o `apiGet/apiPost`
- Lógica de estado con `loading/error` que debería estar en un hook

**Violaciones de estilos de severidad/estado**:
- Clases CSS o colores de severidad/estado hardcodeados fuera de `SeverityBadge` o `StatusBadge`

---

## Output esperado

```
BACKEND
-------
✅ Routers: sin violaciones
⚠️  app/api/risks.py:45 — lógica de cálculo detectada fuera del service
✅ Schemas: sin violaciones
✅ Models: sin violaciones

FRONTEND
--------
✅ Pages: sin violaciones
⚠️  src/components/RiskCard.jsx:23 — llamada directa a fetch()
✅ Badges: sin violaciones
```
