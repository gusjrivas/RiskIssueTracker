# /new-migration

Genera el comando Alembic correcto y valida que la migración cumple las convenciones del proyecto.

## Uso

```
/new-migration name=<descripcion_breve>
```

Ejemplo: `/new-migration name=add_category_to_risks`

---

## Pasos de ejecución

1. **Formatear el nombre**: convertir a snake_case si no lo está.

2. **Mostrar el comando exacto a ejecutar**:
   ```bash
   cd backend && alembic revision --autogenerate -m "<name>"
   ```

3. **Recordar precondiciones**:
   - El servicio de base de datos debe estar corriendo (`docker compose up db`)
   - La variable `DATABASE_URL` debe apuntar a la DB correcta
   - Todos los modelos nuevos deben estar importados en `migrations/env.py`

4. **Checklist de convenciones** — verificar en el archivo generado:

   - [ ] Toda tabla nueva tiene `id UUID DEFAULT uuid_generate_v4()`
   - [ ] Toda tabla nueva tiene `created_at TIMESTAMPTZ DEFAULT NOW()`
   - [ ] Toda tabla nueva tiene `updated_at TIMESTAMPTZ DEFAULT NOW()`
   - [ ] Toda FK tiene `index=True` en el modelo SQLAlchemy
   - [ ] Columnas de filtro frecuente (`status`, `severity`, `project_id`) tienen índice
   - [ ] Los ENUMs nuevos están creados en PostgreSQL (no solo en Python)
   - [ ] `history_entries` y `audit_log` no tienen FKs explícitas hacia otras tablas
   - [ ] La migración tiene función `downgrade()` implementada

5. **Recordar**: nunca editar una migración que ya fue aplicada en `main`.
