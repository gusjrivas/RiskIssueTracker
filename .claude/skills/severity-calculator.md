# Skill: Severity Calculator

La severidad se calcula en **dos pasos** usando la metodología de la empresa.
La implementación canónica está en `backend/app/services/severity_calculator.py`.

---

## Paso 1 — Exposición

`exposure = probability_weight × impact_weight`

### Pesos de Probabilidad

| Nivel | Valor enum | Peso |
|---|---|---|
| Muy baja | `muy_baja` | 0.10 |
| Baja | `baja` | 0.30 |
| Media | `media` | 0.50 |
| Alta | `alta` | 0.70 |
| Muy Alta | `muy_alta` | 0.90 |

### Pesos de Impacto

| Nivel | Valor enum | Peso |
|---|---|---|
| Muy bajo | `muy_bajo` | 0.056 |
| Bajo | `bajo` | 0.10 |
| Medio | `medio` | 0.20 |
| Alto | `alto` | 0.40 |
| Muy Alto | `muy_alto` | 0.80 |

### Matriz de exposición resultante (referencia)

```
             Muy Bajo  Bajo   Medio  Alto   Muy Alto
Muy Alta:      0.05    0.09   0.18   0.36   0.72
Alta:          0.04    0.07   0.14   0.28   0.56
Media:         0.03    0.05   0.10   0.20   0.40
Baja:          0.02    0.03   0.06   0.12   0.24
Muy Baja:      0.01    0.01   0.02   0.04   0.08
```

---

## Paso 2 — Zona de exposición

| Zona | Rango de exposición |
|---|---|
| `bajo` | ≤ 0.09 |
| `medio` | 0.10 – 0.24 |
| `alto` | ≥ 0.28 |

---

## Paso 3 — Severidad

`severity = MATRIX[proximity][exposure_zone]`  → entero ordinal **1–9** (1 = más crítico)

```
                  Zona Bajo   Zona Medio   Zona Alto
corto_plazo:          5           2            1
mediano_plazo:        7           4            3
largo_plazo:          9           8            6
```

Priorización: rojo (1–3) → amarillo (4–6) → verde (7–9)

---

## Funciones disponibles

```python
get_exposure(probability: ProbabilityLevel, impact: ImpactLevel) -> float
get_exposure_zone(exposure: float) -> ExposureZone
get_severity(probability, impact, proximity) -> int   # 1-9
```

---

## Ejemplo

```
probability = muy_alta  → 0.90
impact      = alto      → 0.40
exposure    = 0.90 × 0.40 = 0.36 → zona alto
proximity   = corto_plazo
severity    = MATRIX[corto_plazo][alto] = 1  (CRÍTICO)
```
