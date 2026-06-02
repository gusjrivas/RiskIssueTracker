# Prompt 02 — Setup TDD y calculadora de severidad

## Contexto
Configuración del framework de testing y primeros tests de la calculadora de severidad siguiendo TDD estricto (rojo → verde → refactor).

## Prompts

### Setup de testing
```
Configurá el entorno de testing completo para backend y frontend:

Backend:
- pytest con pytest-cov (cobertura mínima 80%)
- Tests unitarios en tests/unit/ (sin base de datos)
- Tests de integración en tests/integration/ (SQLite en memoria)
- conftest.py con fixtures reutilizables

Frontend:
- Vitest con jsdom
- @testing-library/react
- MSW para mocking de API
- Cobertura mínima 80%

Actualizá CLAUDE.md con la regla: todo código nuevo requiere tests.
Flujo siempre: test rojo → implementación mínima → verde → refactor.
```

### Calculadora de severidad (TDD)
```
Implementá la calculadora de severidad siguiendo TDD:

1. Primero escribí los tests en tests/unit/services/test_severity_calculator.py
   cubriendo todos los casos de la matriz (27 combinaciones de proximidad × zona)
   
2. Luego implementá la lógica mínima en app/services/severity_calculator.py
   con las funciones: get_exposure(), get_exposure_zone(), get_severity()
   
3. Los tests deben pasar al 100%

La calculadora es la única fuente de verdad de la fórmula —
ningún otro módulo debe replicarla.
```

## Branch
`feat/project-setup-complete`

## Resultado
- 42 tests de severidad pasando
- Configuración pytest y vitest completa
- Skill `testing.md` documentando los patrones TDD del proyecto
