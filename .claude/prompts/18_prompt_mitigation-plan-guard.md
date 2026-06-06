# Prompt 18 — Hotfix: bug en guardado del plan de mitigación

## Contexto
Bug en `MitigationPlanPanel`: al presionar Enter en el textarea o al hacer clic en Guardar aparecía un mensaje de error. Además, al salir de la página con cambios sin guardar no se advertía al usuario.

## Branch
`fix/mitigation-plan-save-guard`

## Prompts

### Reporte del bug
```
se debe corregir un bug en guardar plan siempre se muestra un mensaje de error 
al introducir un enter en el text box y al guardar también sale el mismo error. 
La funcionalidad lo que debe hacer es que si el usuario introduce cambios en el 
plan y quiere salir de la pagina le pregunte si quiere guardar los cambios o no 
a si presiona aceptar al mensaje se guardan los cambios.
```

### Regla de workflow
```
antes necesitamos seguir con mas mejoras, pero para estos cambios se necesita 
siempre crear un branch nuevo y generar un PR el cual yo tengo que aprobar 
manualmente antes de hacer un MR a main
```

## Diagnóstico

**Causa raíz del error al guardar:** El `isDirty` comparaba el valor actual contra `initialMitigation`/`initialContingency` (props). Después de un guardado exitoso, las props no cambian, por lo que `isDirty` seguía en `true` y el error del hook se mostraba aunque el save hubiera sido exitoso.

**Causa raíz del crash de navegación:** La versión anterior usaba `useBlocker` de React Router v6, que solo funciona con `createBrowserRouter` (data router). La app usa `BrowserRouter`, por lo que tiraba `Uncaught Error: useBlocker must be used within a data router`, dejando la página en blanco.

## Fix

### Estado de valores guardados
```jsx
// Antes: comparaba contra props (no se actualizaban al guardar)
const isDirty = mitigation !== initialMitigation || contingency !== initialContingency

// Después: estado separado que se actualiza tras cada save exitoso
const [savedMitigation, setSavedMitigation] = useState(initialMitigation)
const [savedContingency, setSavedContingency] = useState(initialContingency)
const isDirty = !readOnly && (mitigation !== savedMitigation || contingency !== savedContingency)

const executeSave = async () => {
  await save({ mitigation_strategy: mitigation, contingency_plan: contingency })
  setSavedMitigation(mitigation)   // dirty flag se resetea correctamente
  setSavedContingency(contingency)
}
```

### Reemplazo de useBlocker por listener DOM
```jsx
// useBlocker eliminado — incompatible con BrowserRouter

// Interceptar clicks en <a href="/..."> mientras hay cambios pendientes
useEffect(() => {
  if (!isDirty) return
  const handleClick = (e) => {
    const anchor = e.target.closest('a[href]')
    if (!anchor) return
    const href = anchor.getAttribute('href')
    if (href && href.startsWith('/')) {
      e.preventDefault()
      e.stopPropagation()
      setPendingHref(href)   // muestra modal
    }
  }
  document.addEventListener('click', handleClick, true)   // capture phase
  return () => document.removeEventListener('click', handleClick, true)
}, [isDirty])
```

### Modal de 3 opciones
```jsx
{pendingHref && (
  <div className="fixed inset-0 z-50 ...">
    <button onClick={() => setPendingHref(null)}>Cancelar</button>
    <button onClick={handleDiscardAndLeave}>Salir sin guardar</button>
    <button onClick={handleSaveAndLeave}>Guardar y salir</button>
  </div>
)}
```

### Guard para navigate() en páginas padre
```jsx
// Prop onDirtyChange para que la página padre conozca el estado dirty
<MitigationPlanPanel onDirtyChange={setPlanDirty} ... />

// En RiskDetailPage / IssuesPage — botón de volver atrás
<button onClick={() => {
  if (planDirty && !window.confirm('Tenés cambios sin guardar en el plan. ¿Salir de todas formas?')) return
  navigate(-1)
}}>
```

## Resultado
- Enter en textarea no genera error
- Guardar resetea el dirty flag correctamente
- Navegar con cambios pendientes muestra modal 3 opciones (Cancelar / Salir sin guardar / Guardar y salir)
- Botón de volver atrás también respeta el estado dirty
- `useBeforeUnload` mantiene la advertencia para cierre de pestaña del navegador
