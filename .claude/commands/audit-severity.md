# /audit-severity

Detecta inconsistencias entre la severidad almacenada en la base de datos y la calculada por la fórmula actual.

## Uso

```
/audit-severity
```

---

## Pasos de ejecución

1. **Leer todos los Risks** de la base de datos que no estén en estado `closed` o `derived`.

2. **Recalcular** para cada Risk:
   ```python
   from app.services.severity_calculator import get_severity
   calculated = get_severity(risk.probability, risk.impact, risk.proximity)
   ```

3. **Comparar** `risk.severity` (almacenado) vs `calculated` (recalculado).

4. **Reportar inconsistencias**:
   ```
   Risk ID: {id}
   Título:  {title}
   Proyecto: {project_name}
   Almacenado: {risk.severity}
   Calculado:  {calculated}
   Campos: probability={prob}, impact={impact}, proximity={prox}
   ```

5. **Resumen final**:
   ```
   Total revisados: N
   Consistentes:    N
   Inconsistentes:  N  ← requieren corrección
   ```

---

## Cuándo ejecutar

- Después de modificar la fórmula de cálculo de severidad
- Antes de una release que afecte la lógica de severidad
- Si se sospecha corrupción de datos
- Como paso de validación en migraciones que afecten `probability`, `impact` o `proximity`

---

## Corrección

Si hay inconsistencias, ejecutar el endpoint (cuando exista):
```
POST /api/v1/admin/recalculate-severities
```
O corregir manualmente con una migración de datos.
