# Skill: Run Local

Levanta la aplicación completa (PostgreSQL + FastAPI + React) usando Docker Compose.

---

## Prerrequisitos

- Docker Desktop corriendo
- Archivo `.env` en la raíz del repo (copiá `.env.example` y completá los valores)

```bash
cp .env.example .env
# Editá .env — al menos AUTH_SECRET_KEY debe ser un valor seguro
```

---

## Primer arranque

```bash
# Construir imágenes y levantar todos los servicios
docker compose up --build
```

Docker ejecuta en orden:
1. **db** — PostgreSQL 16, aplica `database/init.sql` automáticamente al iniciar por primera vez
2. **api** — FastAPI con hot-reload en http://localhost:8000
3. **frontend** — Vite dev server en http://localhost:3000

---

## Arranques siguientes

```bash
# Sin rebuilder (más rápido si no cambiaron dependencias)
docker compose up

# En background
docker compose up -d
```

---

## Verificación de salud

```bash
# API health check
curl -s http://localhost:8000/health

# Docs interactivos
# http://localhost:8000/docs

# Frontend
# http://localhost:3000
```

Respuesta esperada del health check:
```json
{"status": "ok"}
```

---

## Crear primer usuario admin

La app requiere que el primer admin sea aprobado manualmente en la DB.

```bash
# 1. Registrar el usuario via API
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin1234!","full_name":"Admin"}'

# 2. Aprobarlo y darle rol admin directo en la DB
docker compose exec db psql -U riskuser -d risktracker -c \
  "UPDATE users SET status='active', role='admin' WHERE email='admin@test.com';"
```

---

## Detener la app

```bash
# Detener (conserva datos del volumen postgres_data)
docker compose down

# Detener y borrar volúmenes (reset completo de DB)
docker compose down -v
```

---

## Logs y debug

```bash
# Logs de todos los servicios
docker compose logs -f

# Solo el backend
docker compose logs -f api

# Solo la DB
docker compose logs -f db
```

---

## Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `api` se reinicia en loop | DB no está lista aún | Esperar el healthcheck — docker compose tiene `depends_on: condition: service_healthy` |
| `relation "users" does not exist` | `init.sql` no se ejecutó (volumen ya existía) | `docker compose down -v` y volver a levantar |
| Frontend no conecta al backend | `VITE_API_URL` incorrecto | Verificar `docker-compose.yml` — debe ser `http://localhost:8000` |
| `AUTH_SECRET_KEY` warning | Variable no seteada en `.env` | Copiar `.env.example` → `.env` y completar `AUTH_SECRET_KEY` |
| Puerto 5432/8000/3000 ocupado | Otro proceso usando el puerto | `docker compose down` primero; o cambiar el puerto en `docker-compose.yml` |

---

## Variables de entorno requeridas

Ver [.env.example](../../.env.example) para la lista completa. Mínimo necesario:

```env
AUTH_SECRET_KEY=un-secreto-largo-y-aleatorio
```

`DATABASE_URL` y `GOOGLE_CLIENT_ID` ya tienen defaults funcionales en `docker-compose.yml`.
