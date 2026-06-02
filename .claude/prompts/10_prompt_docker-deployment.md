# Prompt 10 — Docker y deployment local

## Contexto
Verificación y corrección de los archivos Docker para que el proyecto funcione completamente con `docker compose up`.

## Prompts

### Verificación de Docker
```
listo ahora verifica que están todos los dokerfiles correctos como para levantar 
una instancia de la aplicacion en local
```

### Bugs de Docker encontrados y corregidos

#### 1. `database/init.sql` desincronizado con modelos SQLAlchemy
- `users.avatar_url` en SQL vs `picture` en el modelo → renombrado a `picture`
- `projects.owner_id` (nullable) vs `created_by NOT NULL` en modelo → corregido
- `risks` faltaba `created_by UUID NOT NULL` → agregado
- `issues` faltaba `created_by UUID NOT NULL` → agregado
- `risks/issues` tenían columnas obsoletas → eliminadas: `root_cause`, `application_team`, `exposure`, `exposure_zone`, `client_notification`
- Enum `exposure_zone` definido pero no usado en ninguna tabla → eliminado

#### 2. Backend Dockerfile sin CMD
```dockerfile
# Agregado al final del Dockerfile:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3. Variables de entorno faltantes en docker-compose
```yaml
# Agregado al servicio api:
AUTH_SECRET_KEY: ${AUTH_SECRET_KEY:-change-me-in-development}
GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:-}
```

### Creación de .env.example
```
Creá un .env.example con todas las variables requeridas documentadas.
```

### Levantar la app para probar
```
levantá en local la app para poder probarla
```

### Bugs de runtime encontrados al levantar

#### 4. Build fallaba: `setuptools.backends.legacy` incompatible con pip 26
```
# En pyproject.toml:
# Antes:
build-backend = "setuptools.backends.legacy:build"
# Después:
build-backend = "setuptools.build_meta"
```

#### 5. Error UUID en producción: `AttributeError: 'UUID' object has no attribute 'replace'`
- `native_uuid=False` en modelos le indica a SQLAlchemy que espere strings
- psycopg2 devuelve objetos UUID nativos desde PostgreSQL → crash
- Corregido: `native_uuid=True` en los 6 modelos

## Branch
`feat/frontend` → luego hotfix

## Resultado
- `docker compose up --build` funciona sin errores
- API en http://localhost:8000, frontend en http://localhost:3000
- `.env.example` con todas las variables documentadas
- Volúmenes configurados para hot-reload (backend y frontend)
