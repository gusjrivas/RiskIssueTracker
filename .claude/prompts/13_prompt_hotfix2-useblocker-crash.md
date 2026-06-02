# Prompt 13 — Hotfix 2: crash pantalla en blanco al abrir riesgo

## Contexto
Bug crítico: al seleccionar un riesgo desde la lista, la pantalla aparecía completamente en blanco.

## Branch
`hotfix2/useBlocker-crash`

## Prompt
```
cuando seleccion un riesgo se ve la pagina en blNCO REVISA SI HAY UN BUG Y CORREGILO 
SI ES ASI CREA UN BRANH HOTFIX2
```

## Diagnóstico

**Error en consola del navegador:**
```
useBlocker must be used within a data router.
See https://reactrouter.com/v6/routers/picking-a-router.
```

**Causa raíz:** `useBlocker` de React Router v6 solo funciona con `createBrowserRouter` (data router). La app usa `BrowserRouter` (non-data router), lo que causaba que el componente `MitigationPlanPanel` tirara un error no capturado que dejaba toda la pantalla en blanco — no solo el panel.

`RiskDetailPage` e `IssuesPage` incluyen `MitigationPlanPanel`, por lo que ambas páginas quedaban en blanco.

## Fix

Reemplazar `useBlocker` por un listener manual que funciona con cualquier router:

```jsx
// Eliminado:
import { useBlocker } from 'react-router-dom'
const blocker = useBlocker(isDirty)
useEffect(() => {
  if (blocker.state === 'blocked') { ... }
}, [blocker])

// Reemplazado por:
useEffect(() => {
  if (!isDirty) return
  const handleClick = (e) => {
    const anchor = e.target.closest('a[href], button')
    if (!anchor) return
    const href = anchor.getAttribute('href')
    if (href?.startsWith('/') && !window.confirm('Tenés cambios sin guardar...')) {
      e.preventDefault()
      e.stopPropagation()
    }
  }
  document.addEventListener('click', handleClick, true)
  return () => document.removeEventListener('click', handleClick, true)
}, [isDirty])
```

`useBeforeUnload` se mantiene para el cierre de pestaña del navegador (no requiere data router).

## Resultado
- Pantalla de detalle de riesgo e issue vuelven a funcionar
- La advertencia de cambios sin guardar sigue operativa (listener + useBeforeUnload)
- Sin errores de JavaScript en consola
