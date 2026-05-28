# /calc-severity

Calcula la exposición y severidad de un riesgo usando la metodología de la empresa.

## Uso

```
/calc-severity probability=<nivel> impact=<nivel> proximity=<plazo>
```

### Valores válidos

- `probability`: `muy_baja` | `baja` | `media` | `alta` | `muy_alta`
- `impact`: `muy_bajo` | `bajo` | `medio` | `alto` | `muy_alto`
- `proximity`: `corto_plazo` | `mediano_plazo` | `largo_plazo`

---

## Pasos de ejecución

1. **Validar** que los tres parámetros tienen valores válidos.

2. **Obtener pesos**:
   - Probability weights: muy_baja=0.10, baja=0.30, media=0.50, alta=0.70, muy_alta=0.90
   - Impact weights: muy_bajo=0.056, bajo=0.10, medio=0.20, alto=0.40, muy_alto=0.80

3. **Calcular exposición**: `exposure = probability_weight × impact_weight`

4. **Determinar zona**:
   - `bajo`:  exposure ≤ 0.09
   - `medio`: 0.10 ≤ exposure ≤ 0.24
   - `alto`:  exposure ≥ 0.28

5. **Lookup severidad** en la matriz:

   ```
                     Zona Bajo   Zona Medio   Zona Alto
   corto_plazo:          5           2            1
   mediano_plazo:        7           4            3
   largo_plazo:          9           8            6
   ```

6. **Devolver**: exposure (4 decimales), zona, severidad (1-9), y prioridad (🔴 1-3 / 🟡 4-6 / 🟢 7-9).

---

## Ejemplos

### Ejemplo 1: Riesgo crítico

```
/calc-severity probability=muy_alta impact=alto proximity=corto_plazo
```

Cálculos:
- probability_weight = 0.90
- impact_weight      = 0.40
- exposure           = 0.90 × 0.40 = **0.3600**
- zona               = **alto** (≥ 0.28)
- severity           = MATRIX[corto_plazo][alto] = **1** 🔴

---

### Ejemplo 2: Riesgo bajo

```
/calc-severity probability=baja impact=bajo proximity=largo_plazo
```

Cálculos:
- probability_weight = 0.30
- impact_weight      = 0.10
- exposure           = 0.30 × 0.10 = **0.0300**
- zona               = **bajo** (≤ 0.09)
- severity           = MATRIX[largo_plazo][bajo] = **9** 🟢

---

### Ejemplo 3: Riesgo medio

```
/calc-severity probability=media impact=medio proximity=mediano_plazo
```

Cálculos:
- probability_weight = 0.50
- impact_weight      = 0.20
- exposure           = 0.50 × 0.20 = **0.1000**
- zona               = **medio** (0.10 – 0.24)
- severity           = MATRIX[mediano_plazo][medio] = **4** 🟡
