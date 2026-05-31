# RiskIssueTracker

Aplicación web para la gestión de riesgos e issues en proyectos. Permite registrar riesgos, calcular su severidad automáticamente, derivarlos a issues cuando se materializan, definir planes de mitigación y contingencia, y mantener un historial completo de cambios con auditoría de todas las acciones.

**Autores:** Gustavo Julián Rivas · Rodolfo Di Chiazza

---

## Tabla de contenidos

1. [Stack tecnológico](#stack-tecnológico)
2. [Arquitectura](#arquitectura)
3. [Requisitos previos](#requisitos-previos)
4. [Levantar el proyecto](#levantar-el-proyecto)
5. [Primer usuario admin](#primer-usuario-admin)
6. [Variables de entorno](#variables-de-entorno)
7. [Estructura del proyecto](#estructura-del-proyecto)
8. [API Reference](#api-reference)
9. [Cálculo de severidad](#cálculo-de-severidad)
10. [Testing](#testing)
11. [Comandos útiles](#comandos-útiles)

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| **Backend** | Python 3.11 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · Alembic |
| **Base de datos** | PostgreSQL 16 |
| **Autenticación** | JWT (HS256) · Google OAuth (opcional) |
| **Frontend** | React 18 · React Router v6 · Vite 5 · Tailwind CSS 3 · Framer Motion |
| **Infraestructura** | Docker Compose |
| **Testing** | pytest · Vitest · Playwright |

---

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│                  Docker Compose                  │
│                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │  frontend  │  │    api     │  │     db     │ │
│  │  :3000     │→ │  :8000     │→ │  :5432     │ │
│  │  React/Vite│  │  FastAPI   │  │ PostgreSQL │ │
│  └────────────┘  └────────────┘  └────────────┘ │
└─────────────────────────────────────────────────┘
```

**Backend (capas):**
- `api/` — Routers HTTP: solo reciben/devuelven JSON, sin lógica de negocio
- `services/` — Toda la lógica de negocio (cálculo de severidad, transiciones, derivación)
- `models/` — Modelos SQLAlchemy (estructura de tablas)
- `schemas/` — Schemas Pydantic (validación y serialización)

**Flujo de un riesgo:**

```
open → in_progress → closed          (riesgo mitigado)
open → in_progress → derived         (riesgo materializado → Issue creado y vinculado)
```

---

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
- Git

> No se necesita Python, Node.js ni PostgreSQL instalados localmente. Todo corre dentro de Docker.

---

## Levantar el proyecto

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd RiskIssueTracker
```

### 2. Crear el archivo de entorno

```bash
cp .env.example .env
```

Editá `.env` y cambiá al menos `AUTH_SECRET_KEY` por un valor seguro:

```env
AUTH_SECRET_KEY=mi-clave-secreta-larga-y-aleatoria
```

### 3. Construir e iniciar los servicios

```bash
docker compose up --build
```

Este comando:
1. Construye las imágenes de `api` y `frontend`
2. Levanta PostgreSQL y aplica `database/init.sql` automáticamente (solo la primera vez)
3. Inicia la API con hot-reload en `http://localhost:8000`
4. Inicia el frontend con Vite HMR en `http://localhost:3000`

> La primera vez tarda unos minutos por la descarga de imágenes y la instalación de dependencias.

### 4. Verificar que todo esté corriendo

```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

También podés abrir:
- **Frontend:** http://localhost:3000
- **API Docs (Swagger):** http://localhost:8000/docs

### Arranques siguientes

```bash
# Con reconstrucción (cuando cambian dependencias en pyproject.toml o package.json)
docker compose up --build

# Sin reconstrucción (más rápido, para cambios solo en código)
docker compose up

# En segundo plano
docker compose up -d
```

---

## Primer usuario admin

Al registrarte por primera vez, tu cuenta queda en estado `pending`. Para activarla y darle rol admin hay que hacerlo directamente en la base de datos:

### Paso 1 — Registrarse

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ejemplo.com","password":"MiClave123!","full_name":"Mi Nombre"}'
```

O hacerlo desde la pantalla de login en http://localhost:3000.

### Paso 2 — Aprobar desde la base de datos

```bash
docker compose exec db psql -U riskuser -d risktracker -c \
  "UPDATE users SET status='active', role='admin' WHERE email='admin@ejemplo.com';"
```

### Paso 3 — Iniciar sesión

Abrí http://localhost:3000 e ingresá con el email y contraseña registrados.

Una vez dentro como admin, podés aprobar a los demás usuarios desde el link **Administración** en el header del dashboard. No es necesario volver a la base de datos para usuarios siguientes.

---

## Variables de entorno

Todas las variables se definen en `.env` (copiado desde `.env.example`).

| Variable | Requerida | Descripción | Default |
|---|---|---|---|
| `AUTH_SECRET_KEY` | **Sí** | Clave para firmar tokens JWT. Cambiar en producción. | `change-me-in-development` |
| `AUTH_ALGORITHM` | No | Algoritmo JWT | `HS256` |
| `AUTH_TOKEN_EXPIRE_MINUTES` | No | Duración del token en minutos | `1440` (24 h) |
| `GOOGLE_CLIENT_ID` | No | Client ID de Google OAuth. Dejar vacío para deshabilitar. | *(vacío)* |
| `DATABASE_URL` | No | URL de conexión a PostgreSQL | Sobreescrita por docker-compose |
| `ENVIRONMENT` | No | `development` o `production` | `development` |

> `DATABASE_URL` es sobreescrita automáticamente por `docker-compose.yml` con la URL interna del contenedor. Solo es necesario cambiarla si corrés la API fuera de Docker.

---

## Estructura del proyecto

```
RiskIssueTracker/
├── backend/
│   ├── app/
│   │   ├── api/               # Routers HTTP (auth, projects, risks, issues, history, admin)
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── schemas/           # Schemas Pydantic + Enums del dominio
│   │   ├── services/          # Lógica de negocio
│   │   ├── db/                # Engine y sesión de base de datos
│   │   ├── config.py          # Settings con pydantic-settings
│   │   └── main.py            # Instancia FastAPI, CORS, routers, /health
│   ├── migrations/            # Migraciones Alembic
│   ├── tests/
│   │   ├── unit/              # Tests unitarios (sin DB)
│   │   └── integration/       # Tests de integración (DB SQLite en memoria)
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/               # Funciones de llamada HTTP (client.js + módulo por entidad)
│   │   ├── components/        # Componentes reutilizables (badges, cards, forms, timeline)
│   │   ├── hooks/             # Hooks de estado + llamadas a la API
│   │   ├── pages/             # Páginas completas (una por ruta)
│   │   ├── utils/             # Utilidades (severityCalc.js — fórmula de severidad en JS)
│   │   └── __tests__/         # Tests de componentes y hooks
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
├── database/
│   ├── init.sql               # DDL completo — aplicado automáticamente al crear la DB
│   └── seeds.sql              # Datos de prueba opcionales
├── docker-compose.yml
├── .env.example               # Plantilla de variables de entorno
└── README.md
```

---

## API Reference

**Base URL:** `http://localhost:8000/api/v1`

> La documentación interactiva completa (Swagger UI) está disponible en `http://localhost:8000/docs`.

### Autenticación

Todos los endpoints protegidos requieren el header:

```
Authorization: Bearer <token>
```

El token se obtiene al hacer login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ejemplo.com","password":"MiClave123!"}'
# → {"access_token":"eyJ...", "token_type":"bearer"}
```

### Endpoints

| Método | Ruta | Descripción | Auth |
|---|---|---|---|
| `GET` | `/health` | Health check | — |
| `POST` | `/auth/register` | Registrar usuario (queda `pending`) | — |
| `POST` | `/auth/login` | Iniciar sesión, devuelve JWT | — |
| `GET` | `/auth/me` | Datos del usuario autenticado | ✓ |
| `GET` | `/projects` | Listar proyectos | ✓ |
| `POST` | `/projects` | Crear proyecto | ✓ |
| `PATCH` | `/projects/{id}` | Actualizar proyecto | ✓ |
| `DELETE` | `/projects/{id}` | Eliminar proyecto | ✓ |
| `GET` | `/risks` | Listar riesgos (`?project_id=&status=&category=`) | ✓ |
| `POST` | `/risks` | Crear riesgo (severidad calculada automáticamente) | ✓ |
| `GET` | `/risks/{id}` | Detalle de riesgo | ✓ |
| `PATCH` | `/risks/{id}` | Actualizar riesgo | ✓ |
| `PATCH` | `/risks/{id}/status` | Cambiar estado del riesgo | ✓ |
| `DELETE` | `/risks/{id}` | Eliminar riesgo | ✓ |
| `GET` | `/issues` | Listar issues (`?project_id=&status=`) | ✓ |
| `POST` | `/issues` | Crear issue manualmente | ✓ |
| `POST` | `/issues/derive` | Derivar issue desde un riesgo (`{"risk_id":"..."}`) | ✓ |
| `GET` | `/issues/{id}` | Detalle de issue | ✓ |
| `PATCH` | `/issues/{id}` | Actualizar issue | ✓ |
| `PATCH` | `/issues/{id}/status` | Cambiar estado del issue | ✓ |
| `DELETE` | `/issues/{id}` | Eliminar issue | ✓ |
| `GET` | `/history/{entity_type}/{entity_id}` | Historial de transiciones de estado | ✓ |
| `GET` | `/admin/users` | Listar usuarios | ✓ Admin |
| `PATCH` | `/admin/users/{id}` | Editar datos de usuario | ✓ Admin |
| `PATCH` | `/admin/users/{id}/approve` | Aprobar usuario | ✓ Admin |
| `PATCH` | `/admin/users/{id}/deactivate` | Desactivar usuario | ✓ Admin |
| `GET` | `/admin/audit-log` | Ver log de auditoría completo | ✓ Admin |

### Paginación

Todos los endpoints de lista aceptan `?page=1&size=20` y devuelven:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

---

## Cálculo de severidad

La severidad de un riesgo se calcula automáticamente en el backend al crearlo o actualizarlo, usando una fórmula de dos pasos. El frontend también la calcula en tiempo real mientras se completa el formulario.

### Paso 1 — Exposición

```
exposición = peso_probabilidad × peso_impacto
```

| Probabilidad | Peso | | Impacto | Peso |
|---|---|---|---|---|
| Muy baja | 0.056 | | Muy bajo | 0.10 |
| Baja | 0.10 | | Bajo | 0.30 |
| Media | 0.20 | | Medio | 0.50 |
| Alta | 0.40 | | Alto | 0.70 |
| Muy alta | 0.80 | | Muy alto | 0.90 |

**Zonas de exposición:**
- `bajo`: exposición ≤ 0.09
- `medio`: 0.10 ≤ exposición ≤ 0.24
- `alto`: exposición ≥ 0.28

### Paso 2 — Severidad (1 = más crítico, 9 = menos crítico)

| Proximidad | Zona Bajo | Zona Medio | Zona Alto |
|---|---|---|---|
| Corto plazo | 5 | 2 | **1** |
| Mediano plazo | 7 | 4 | 3 |
| Largo plazo | 9 | 8 | 6 |

**Ejemplo:** Probabilidad Alta (0.40) × Impacto Alto (0.70) = **0.28** → Zona Alto + Corto plazo = **Severidad 1 (Crítico)**

---

## Testing

### Backend

```bash
cd backend

# Todos los tests
pytest

# Con reporte de cobertura (mínimo 80% requerido)
pytest --cov=app --cov-report=term-missing

# Solo tests unitarios (sin base de datos)
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v
```

> Los tests de integración usan SQLite en memoria. No requieren PostgreSQL corriendo.

### Frontend

```bash
cd frontend

# Tests en modo watch (desarrollo)
npm run test

# Tests una sola vez
npm run test:run

# Con reporte de cobertura
npm run coverage
```

---

## Comandos útiles

### Docker

```bash
# Ver estado de los contenedores
docker compose ps

# Ver logs en tiempo real (todos los servicios)
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f db

# Reiniciar todos los servicios (sin reconstruir)
docker compose restart

# Detener y conservar datos
docker compose down

# Detener y eliminar todos los datos (reset completo de la DB)
docker compose down -v

# Reconstruir y reiniciar un servicio específico
docker compose up --build -d frontend
docker compose up --build -d api
```

### Base de datos

```bash
# Acceder a la consola de PostgreSQL
docker compose exec db psql -U riskuser -d risktracker

# Listar todos los usuarios
docker compose exec db psql -U riskuser -d risktracker -c \
  "SELECT email, full_name, status, role FROM users;"

# Aprobar un usuario manualmente
docker compose exec db psql -U riskuser -d risktracker -c \
  "UPDATE users SET status='active' WHERE email='usuario@ejemplo.com';"

# Promover a admin
docker compose exec db psql -U riskuser -d risktracker -c \
  "UPDATE users SET status='active', role='admin' WHERE email='usuario@ejemplo.com';"
```

### Migraciones (Alembic)

```bash
cd backend

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Ver estado actual
alembic current

# Ver historial de migraciones
alembic history

# Generar nueva migración (después de cambiar modelos SQLAlchemy)
alembic revision --autogenerate -m "descripción del cambio"
```

---

## Licencia

Uso interno — todos los derechos reservados.
© 2026 Gustavo Julián Rivas · Rodolfo Di Chiazza
