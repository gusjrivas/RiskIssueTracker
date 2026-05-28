# RiskIssueTracker — CLAUDE.md

## Propósito del proyecto

Aplicación web para la gestión de riesgos y problemas (risks & issues) organizados por proyecto/cliente. Permite registrar riesgos, calcular su severidad usando la metodología de la empresa, derivarlos a issues cuando se materializan, definir planes de mitigación y contingencia, y mantener un historial completo de cambios con auditoría de todas las acciones.

---

## Folder Map

```
RiskIssueTracker/
├── backend/                        # API FastAPI + lógica de negocio
│   ├── app/
│   │   ├── api/                    # Routers HTTP: solo reciben/devuelven JSON, sin lógica
│   │   ├── models/                 # Modelos SQLAlchemy: solo estructura de tablas
│   │   ├── schemas/                # Schemas Pydantic: validación y serialización
│   │   │   └── common.py           # Enums del dominio + PaginatedResponse (única fuente de verdad)
│   │   ├── services/               # Toda la lógica de negocio
│   │   │   ├── severity_calculator.py  # Fórmula de severidad (única fuente de verdad)
│   │   │   ├── auth_service.py     # JWT, Google OAuth, email/password
│   │   │   └── audit_service.py    # Registro de todas las acciones mutantes
│   │   ├── db/
│   │   │   ├── base.py             # DeclarativeBase de SQLAlchemy
│   │   │   └── session.py          # Engine, SessionLocal, get_db()
│   │   ├── config.py               # Settings con pydantic-settings
│   │   └── main.py                 # Instancia FastAPI, CORS, routers, /health
│   ├── migrations/                 # Migraciones Alembic
│   │   ├── env.py                  # Configuración de autogenerate
│   │   ├── script.py.mako          # Template de migraciones
│   │   └── versions/               # Archivos de migración generados
│   ├── alembic.ini                 # Configuración de Alembic
│   ├── pyproject.toml              # Dependencias del proyecto Python
│   └── Dockerfile                  # Imagen Docker del backend
├── frontend/                       # SPA React + Vite
│   ├── src/
│   │   ├── pages/                  # Vistas completas (una por ruta)
│   │   ├── components/             # Componentes reutilizables
│   │   ├── hooks/                  # Encapsulan llamadas API + estado (loading/error/data)
│   │   └── api/                    # Funciones puras de llamada HTTP
│   ├── index.html                  # Entry point HTML
│   ├── vite.config.js              # Configuración Vite
│   ├── Dockerfile                  # Imagen Docker del frontend
│   └── package.json                # Dependencias npm
├── database/
│   ├── init.sql                    # DDL completo: extensiones, enums, tablas, índices
│   └── seeds.sql                   # Datos de prueba para desarrollo
├── docker-compose.yml              # Orquestación: db + api + frontend
├── .gitignore
└── .claude/
    ├── settings.json               # Permisos y configuración del agente
    ├── rules/
    │   ├── backend.md              # Convenciones de capas backend
    │   ├── frontend.md             # Convenciones de capas frontend
    │   └── database.md             # Convenciones de migraciones y esquema
    ├── skills/
    │   ├── severity-calculator.md  # Fórmula completa (2 pasos: exposición → severidad)
    │   ├── add-endpoint.md         # Checklist para agregar un endpoint completo
    │   ├── backend-practices.md    # SQLAlchemy 2.0, Pydantic v2, JWT, audit
    │   ├── frontend-practices.md   # Hooks, auth, Google OAuth, paginación
    │   ├── status-transitions.md   # Máquina de estados Risk/Issue + flujo derive
    │   └── api-conventions.md      # Errores HTTP, paginación, auth header, códigos
    └── commands/
        ├── calc-severity.md        # /calc-severity
        ├── new-migration.md        # /new-migration
        ├── audit-layers.md         # /audit-layers
        └── audit-severity.md       # /audit-severity
```

---

## Dominio

### Entidades principales

| Entidad | Descripción |
|---|---|
| **User** | Usuario de la aplicación con rol admin o user, autenticable via Google o email/password |
| **Project** | Proyecto o cliente al que pertenecen los riesgos e issues |
| **Risk** | Riesgo identificado con probabilidad, impacto, proximidad, categoría y severidad calculada |
| **Issue** | Problema activo derivado de un Risk no mitigado |
| **HistoryEntry** | Timeline de transiciones de estado (Risk o Issue), append-only |
| **AuditLog** | Registro de TODAS las acciones de cualquier usuario, append-only |

### Estados de Risk

```
open → in_progress → closed    (riesgo mitigado)
open → in_progress → derived   (riesgo materializado → Issue abierto y vinculado)
```

### Estados de Issue

```
open → in_progress → closed
```

### Cálculo de Severidad (2 pasos)

**Paso 1 — Exposición** = `probability_weight × impact_weight`

| Nivel prob/impact | Muy bajo/baja | Bajo/baja | Medio/media | Alto/alta | Muy alto/alta |
|---|---|---|---|---|---|
| Peso | 0.056 / 0.10 | 0.10 / 0.30 | 0.20 / 0.50 | 0.40 / 0.70 | 0.80 / 0.90 |

**Paso 2 — Severidad** = lookup `proximity × exposure_zone` → entero 1–9 (1=más crítico)

```
                  Zona Bajo   Zona Medio   Zona Alto
corto_plazo:          5           2            1
mediano_plazo:        7           4            3
largo_plazo:          9           8            6
```

Zonas: bajo ≤ 0.09 | medio 0.10–0.24 | alto ≥ 0.28

### Categorías de Risk

`calendario` | `alcance` | `ingresos` | `costos` | `presupuesto` | `equipo` | `gestion`

### Roles de usuario

- **admin**: aprueba/desactiva usuarios, accede a endpoints `/admin/*`
- **user**: crea y gestiona risks/issues dentro de sus proyectos asignados

### Flujo de registro de usuarios

1. Usuario se registra (Google OAuth o email/password) → estado `pending`
2. Admin aprueba → estado `active`
3. Admin puede desactivar → estado `inactive` (baja lógica, no se borra)

---

## Paginación

Todos los endpoints de lista usan `?page=1&size=20` y devuelven:
```json
{ "items": [...], "total": N, "page": N, "size": N, "pages": N }
```

---

## Convenciones por capa

- **Backend API**: ver [.claude/rules/backend.md](.claude/rules/backend.md)
- **Frontend**: ver [.claude/rules/frontend.md](.claude/rules/frontend.md)
- **Base de datos**: ver [.claude/rules/database.md](.claude/rules/database.md)

---

## Slash commands disponibles

| Comando | Descripción |
|---|---|
| `/calc-severity` | Calcula exposición y severidad dado probability, impact y proximity |
| `/new-migration` | Genera el comando alembic correcto + checklist de convenciones DB |
| `/audit-layers` | Detecta violaciones de separación de capas en backend y frontend |
| `/audit-severity` | Detecta inconsistencias entre severidad almacenada y fórmula actual |
