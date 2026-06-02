# Prompt 01 — Scaffolding inicial del proyecto

## Contexto
Arranque del proyecto desde cero. Se define la estructura completa, el dominio de negocio y la configuración del agente Claude Code.

## Prompts

### Scaffolding base
```
Creá el scaffolding inicial para una aplicación web de gestión de riesgos e issues por proyecto/cliente.

Stack:
- Backend: Python 3.11, FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic, Pydantic v2
- Frontend: React 18, Vite, Tailwind CSS, React Router v6
- Infraestructura: Docker Compose

Dominio:
- Entidades: User, Project, Risk, Issue, HistoryEntry, AuditLog
- Los riesgos tienen probabilidad, impacto, proximidad y una severidad calculada
- Los riesgos pueden derivarse a Issues cuando se materializan
- Historial append-only de transiciones de estado
- Roles: admin y user

Estructura de carpetas:
- backend/app/{api,models,schemas,services,db}/
- frontend/src/{pages,components,hooks,api}/
- database/init.sql
- docker-compose.yml
- .claude/ con settings, skills, rules y commands

Creá también los archivos de configuración del agente en .claude/:
- settings.json con permisos apropiados
- rules/backend.md, rules/frontend.md, rules/database.md
- skills/ para las convenciones del proyecto
```

### Dominio y metodología de severidad
```
El cálculo de severidad de un riesgo sigue esta metodología:

Paso 1 — Exposición = probability_weight × impact_weight

Pesos de probabilidad: muy_baja=0.056, baja=0.10, media=0.20, alta=0.40, muy_alta=0.80
Pesos de impacto: muy_bajo=0.10, bajo=0.30, medio=0.50, alto=0.70, muy_alto=0.90

Paso 2 — Severidad (1=más crítico, 9=menos crítico)
Zonas: bajo ≤ 0.09 | medio 0.10–0.24 | alto ≥ 0.28

Matriz:
             Zona Bajo   Zona Medio   Zona Alto
corto_plazo:     5           2            1
mediano_plazo:   7           4            3
largo_plazo:     9           8            6

Categorías de riesgo: calendario, alcance, ingresos, costos, presupuesto, equipo, gestion

Implementá esta lógica como única fuente de verdad en backend/app/services/severity_calculator.py
```

### Estados y flujos
```
Máquina de estados para Risk:
- open → in_progress → closed    (riesgo mitigado)
- open → in_progress → derived   (riesgo materializado → Issue creado y vinculado)

Máquina de estados para Issue:
- open → in_progress → closed

Flujo de registro de usuarios:
1. Usuario se registra → estado pending
2. Admin aprueba → estado active
3. Admin puede desactivar → estado inactive (baja lógica, no se borra)
```

## Branch
`feat/project-setup-complete`

## Resultado
- Estructura completa de carpetas y archivos base
- `.claude/settings.json` con permisos
- `.claude/rules/` con convenciones por capa
- `.claude/skills/` con severity calculator, status transitions, API conventions, etc.
- `database/init.sql` con DDL completo
- `docker-compose.yml` base
- `pyproject.toml` y `package.json` con dependencias
