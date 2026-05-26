---
path: backend/migrations/**
---

# Database Rules

## Estructura de tablas

- Toda tabla tiene obligatoriamente: `id` (UUID, generado con `uuid-ossp`), `created_at` (timestamp with time zone, default NOW()), `updated_at` (timestamp with time zone, default NOW()).
- Los tipos de estado y severidad se definen como tipos ENUM en PostgreSQL (definidos en `database/init.sql`).

## Índices

- Crear índice en **todas las foreign keys** (FK).
- Crear índice en todas las columnas usadas frecuentemente en filtros (`status`, `severity`, `project_id`, `entity_type`).

## History entries

- `history_entries` es una tabla **append-only**: solo se hacen INSERT, nunca UPDATE ni DELETE.
- El join con la entidad referenciada se hace por `(entity_type, entity_id)`, sin FK explícitas, para poder referenciar tanto risks como issues desde la misma tabla.

## Migraciones

- Las migraciones se generan **únicamente** con `alembic revision --autogenerate -m "descripción"`.
- **Nunca editar** una migración que ya fue aplicada en `main`.
- `alembic downgrade` requiere aprobación explícita (está en la lista `ask` de settings.json).
- El archivo `database/init.sql` define el esquema inicial para Docker. Las migraciones posteriores se aplican sobre ese base.
