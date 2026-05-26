# Skill: Severity Calculator

## Fórmula de cálculo de severidad

El score de severidad se calcula combinando cuatro factores con pesos distintos:

```
score = (probability * 0.35 + impact * 0.35 + urgency_norm * 0.15 + scope_norm * 0.15) / 5
```

Donde:
- `probability`: valor 1–5 (sin normalizar)
- `impact`: valor 1–5 (sin normalizar)
- `urgency_norm`: urgency (1–3) normalizado a escala 1–5
- `scope_norm`: scope (1–3) normalizado a escala 1–5

## Normalización de urgency y scope

Urgency y scope tienen escala 1–3 y deben normalizarse a 1–5 antes de aplicar la fórmula:

```
valor_norm = 1 + (valor - 1) * (4 / (max - 1))
           = 1 + (valor - 1) * 2
```

Ejemplos:
- urgency=1 → norm=1.0
- urgency=2 → norm=3.0
- urgency=3 → norm=5.0

## Tabla de rangos

| Score | Nivel |
|---|---|
| 0.00 – 0.39 | **LOW** |
| 0.40 – 0.59 | **MEDIUM** |
| 0.60 – 0.79 | **HIGH** |
| 0.80 – 1.00 | **CRITICAL** |

## Implementación

La implementación canónica está en [backend/app/services/severity_calculator.py](../../backend/app/services/severity_calculator.py).

Funciones disponibles:
- `_normalize_to_5(value, max_value)` → float
- `get_severity_score(probability, impact, urgency, scope)` → float
- `score_to_severity(score)` → Severity
- `calculate_severity(probability, impact, urgency, scope)` → Severity
