# Prompt 14 — Hotfix 3: visibilidad de issues, bloqueo de riesgo derivado, crear issue, nombre del proyecto

## Contexto
Cuatro bugs/mejoras encontrados en el testing del sistema en producción local.

## Branch
`hotfix3/issues-visibility-derived-lock`

## Prompts

### Bug 1 — Issues no visibles en la aplicación
```
nuevo bug que encontré ademas de los anteriores. no hay boton de crear un problema 
para los proyecto solo crear riesgo. debes agregar esa funcionalidad.

nuevo bug que encontré es que no se visualiza el problema en la aplicación se deberian 
ver ademas de los riesgos los problemas asociados
```

**Causa:** No existía ninguna vista para listar issues por proyecto. Solo había detalle de un issue individual al que se llegaba indirectamente (al derivar un riesgo o desde el link en el detalle del riesgo).

**Fix:** Transformar `RisksPage` en una página con dos tabs:
- **Tab Riesgos**: lista de riesgos con `RiskCard` y botón "Nuevo riesgo"
- **Tab Issues**: lista de issues con `IssueCard` y botón "Nuevo issue"
- Cada tab muestra el contador de items

Nuevos componentes:
- `IssueCard.jsx`: tarjeta similar a RiskCard pero para issues
- `IssueForm.jsx`: formulario con título, descripción y severidad (selector 1-9)

### Bug 2 — Riesgo derivado sigue siendo editable
```
si un riesgo se conviertió en problema no se debería poder seguir editando el riesgo 
porque se sigue el tracking en el problema
```

**Causa:** `RiskDetailPage` no distinguía el estado `derived` — seguía mostrando `StatusTransitionButton` y `MitigationPlanPanel` editable.

**Fix en RiskDetailPage:**
- Banner informativo con ícono de candado cuando `status=derived`
- Ocultar `StatusTransitionButton` (no se puede cambiar estado)
- `MitigationPlanPanel` con prop `readOnly=true` (textareas grises, botón guardar oculto)
- Etiqueta "(solo lectura)" junto al título del plan

**Fix en MitigationPlanPanel:**
- Nueva prop `readOnly` (default `false`)
- Cuando `readOnly=true`: textareas con `readOnly`, opacidad reducida, botón guardar oculto
- `isDirty` siempre `false` cuando `readOnly=true` (no activa el listener de navegación)

### Bug 3 — Nombre del proyecto no se mostraba
```
otro bug es que se debe visualizar el nombre del proyecto que estoy viendo sus riesgos y problemas
```

**Causa:** `RisksPage` mostraba el texto estático "Proyecto" como título del header.

**Fix:** `useEffect` en `RisksPage` que llama `getProject(projectId)` y muestra `project.name` y `project.client` en el header.

### Botón crear issue (feature)
```
no hay boton de crear un problema para los proyectos solo crear riesgo. 
debes agregar esa funcionalidad.
```

**Implementado:** `IssueForm.jsx` con campos título, descripción y severidad (selector 1-9 con etiquetas Crítico/Moderado/Bajo). Integrado en el tab Issues con botón "Nuevo issue".

## Resultado
- Tab Riesgos / Issues con contador en cada tab
- Issues creables manualmente con formulario
- Riesgos derivados bloqueados con banner y modo solo lectura
- Nombre y cliente del proyecto en el header
