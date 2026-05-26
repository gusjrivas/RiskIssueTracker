# RiskIssueTracker — CLAUDE.md

## Propósito del proyecto

Aplicación web para la gestión de riesgos y problemas (risks & issues) organizados por proyecto/cliente. Permite registrar riesgos, calcular su severidad, derivarlos a issues, definir planes de mitigación con acciones, y mantener un historial completo de cambios de estado.

---

## Folder Map

```
RiskIssueTracker/
├── backend/                        # API FastAPI + lógica de negocio
│   ├── app/
│   │   ├── api/                    # Routers HTTP: solo reciben/devuelven JSON, sin lógica
│   │   ├── models/                 # Modelos SQLAlchemy: solo estructura de tablas
│   │   ├── schemas/                # Schemas Pydantic: validación y serialización
│   │   │   └── common.py           # Enums del dominio (única fuente de verdad)
│   │   ├── services/               # Toda la lógica de negocio
│   │   │   └── severity_calculator.py  # Fórmula de severidad (única fuente de verdad)
│   │   ├── db/
│   │   │   ├── base.py             # DeclarativeBase de SQLAlchemy
│   │   │   └── session.py          # Engine, SessionLocal, get_db()
│   │   ├── config.py               # Settings con pydantic-settings
│   │   └── main.py                 # Instancia FastAPI, CORS, routers, /health
│   ├── migrations/                 # Migraciones Alembic
│   │   └── versions/               # Archivos de migración generados automáticamente
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
    │   └── severity-calculator.md  # Fórmula completa de cálculo de severidad
    └── commands/
        └── calc-severity.md        # Slash command /calc-severity
```

---

## Dominio

### Entidades principales

| Entidad | Descripción |
|---|---|
| **Project** | Proyecto o cliente al que pertenecen los riesgos e issues |
| **Risk** | Riesgo identificado con probabilidad, impacto, urgencia y alcance |
| **Issue** | Problema activo, puede originarse desde un Risk |
| **MitigationPlan** | Plan de mitigación asociado a un Risk o Issue |
| **MitigationAction** | Acción individual dentro de un MitigationPlan |
| **HistoryEntry** | Registro append-only de cambios de estado (Risk o Issue) |

### Estados de Risk

```
open → in_progress → closed
         └──────────────────→ [deriva en Issue]
```

### Estados de Issue

```
open → in_progress → closed
```

### Niveles de severidad

| Nivel | Score |
|---|---|
| **low** | 0.00 – 0.39 |
| **medium** | 0.40 – 0.59 |
| **high** | 0.60 – 0.79 |
| **critical** | 0.80 – 1.00 |

---

## Convenciones por capa

- **Backend API**: ver [.claude/rules/backend.md](.claude/rules/backend.md) — routers, services, models, schemas
- **Frontend**: ver [.claude/rules/frontend.md](.claude/rules/frontend.md) — pages, components, hooks, api/
- **Base de datos**: ver [.claude/rules/database.md](.claude/rules/database.md) — migraciones, índices, history

---

## Slash commands disponibles

| Comando | Descripción |
|---|---|
| `/calc-severity` | Calcula el score y nivel de severidad dado probability, impact, urgency y scope |
