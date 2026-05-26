---
path: frontend/**
---

# Frontend Rules

## Estructura de carpetas

- **`pages/`**: vistas completas asociadas a una ruta (ej. `Dashboard.jsx`, `RisksPage.jsx`). Componen hooks y components, no tienen lógica de fetch directo.
- **`components/`**: componentes reutilizables sin conocimiento de rutas. Reciben props, renderizan UI.
- **`hooks/`**: encapsulan llamadas a `api/` más el estado local (`loading`, `error`, `data`). Son la única forma en que las páginas acceden a datos remotos.
- **`api/`**: funciones puras de llamada HTTP. Solo llaman a `client.js`, no manejan estado.

## Naming

- Componentes: `PascalCase.jsx` (ej. `RiskCard.jsx`, `SeverityBadge.jsx`)
- Hooks: `use{Nombre}.js` (ej. `useRisks.js`, `useMitigationPlan.js`)
- Funciones API: `camelCase` en archivos `camelCase.js` (ej. `risks.js` → `getRisks`, `createRisk`)

## Patrones obligatorios

- Los componentes **no llaman `fetch` directamente**. Toda llamada HTTP pasa por `api/` y se consume desde un hook.
- Cada hook expone exactamente `{ data, loading, error }` (más funciones de mutación si aplica).
- `SeverityBadge` y `StatusBadge` son la **fuente única de verdad** para colores y etiquetas de severidad/estado. Ningún otro componente hardcodea esos estilos.
- Las páginas usan hooks para obtener datos y pasan props a los componentes — no hay fetch en JSX.
