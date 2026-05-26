# /calc-severity

Calcula el score y nivel de severidad de un riesgo o issue.

## Uso

```
/calc-severity probability=<1-5> impact=<1-5> urgency=<1-3> scope=<1-3>
```

## Pasos de ejecución

1. **Validar rangos**:
   - `probability`: entero entre 1 y 5 (inclusive)
   - `impact`: entero entre 1 y 5 (inclusive)
   - `urgency`: entero entre 1 y 3 (inclusive)
   - `scope`: entero entre 1 y 3 (inclusive)
   - Si algún valor está fuera de rango, mostrar error y detener.

2. **Normalizar urgency y scope** a escala 1–5:
   ```
   urgency_norm = 1 + (urgency - 1) * 2
   scope_norm   = 1 + (scope - 1) * 2
   ```

3. **Calcular score**:
   ```
   score = (probability * 0.35 + impact * 0.35 + urgency_norm * 0.15 + scope_norm * 0.15) / 5
   ```

4. **Determinar nivel** según tabla de rangos:
   - 0.00–0.39 → LOW
   - 0.40–0.59 → MEDIUM
   - 0.60–0.79 → HIGH
   - 0.80–1.00 → CRITICAL

5. **Devolver** score (4 decimales) y nivel.

---

## Ejemplos

### Ejemplo 1: Riesgo crítico

```
/calc-severity probability=4 impact=5 urgency=3 scope=3
```

Cálculos:
- urgency_norm = 1 + (3-1)*2 = 5.0
- scope_norm   = 1 + (3-1)*2 = 5.0
- numerador    = 4*0.35 + 5*0.35 + 5*0.15 + 5*0.15
               = 1.40 + 1.75 + 0.75 + 0.75 = 4.65
- score        = 4.65 / 5 = **0.9300**
- nivel        = **CRITICAL**

---

### Ejemplo 2: Riesgo medio

```
/calc-severity probability=2 impact=3 urgency=1 scope=2
```

Cálculos:
- urgency_norm = 1 + (1-1)*2 = 1.0
- scope_norm   = 1 + (2-1)*2 = 3.0
- numerador    = 2*0.35 + 3*0.35 + 1*0.15 + 3*0.15
               = 0.70 + 1.05 + 0.15 + 0.45 = 2.35
- score        = 2.35 / 5 = **0.4700**
- nivel        = **MEDIUM**
