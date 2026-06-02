# Prompt 12 — Mejoras UX

## Contexto
Mejoras de experiencia de usuario: cálculo en tiempo real de severidad, edición de usuarios desde admin, y advertencia de cambios sin guardar.

## Branch
`feat/ux-improvements`

## Prompts

### Las 3 mejoras
```
crear una nueva rama para introducir mejoras en front & backend. 

mejora si el usario ingresa mas comentarios a un plan de mitigación antes de salir 
de la pantalla mostrar un popup que indique que hay cambios sin guardar sino cuando 
sale pierde lo que escribió. 

otra mejora es que el administrador debe ver todos los datos de los usarios es decir 
puede editarlos para cambiar nombre o el mail si el usuario lo ingresó mal. 

otra mejora es que debe calcularse automaticamente el impacto a partir de la probabilidad 
y la cercania como te lo pase segun el documento de especificacion
```

### Clarificación sobre el cálculo automático
Pregunta: ¿Qué debe calcularse automáticamente?
**Respuesta del usuario: "Exposición + Severidad"**

Mostrar en tiempo real: Exposición (float), Zona de exposición (bajo/medio/alto) y Severidad calculada (1-9) mientras el usuario selecciona los campos en el formulario de riesgo.

## Implementación

### Mejora 1 — Severidad en tiempo real (RiskForm)
```
Implementá en el formulario de creación de riesgo un panel de preview
que muestre en tiempo real (mientras el usuario selecciona los campos):
- Exposición = probability_weight × impact_weight
- Zona de exposición (bajo/medio/alto)  
- Severidad calculada (1-9) con SeverityBadge

Creá frontend/src/utils/severityCalc.js con la misma fórmula que el backend.
El panel aparece solo cuando los 3 campos están seleccionados.
```

### Mejora 2 — Edición de usuarios desde AdminPage
```
Backend: agregar PATCH /api/v1/admin/users/{id} con UserAdminUpdate schema
(full_name, email, role — todos opcionales). Validar que el email no esté
en uso por otro usuario.

Frontend: botón de lápiz por fila en AdminPage que despliega formulario
inline con nombre, email y rol. Actualización optimista en el estado local.
```

### Mejora 3 — Advertencia de cambios sin guardar (MitigationPlanPanel)
```
En MitigationPlanPanel:
- Detectar si el contenido cambió respecto al valor guardado
- Mostrar indicador "Cambios sin guardar" en amarillo cuando hay cambios pendientes
- useBeforeUnload: bloquear cierre/recarga de pestaña del navegador
- useBlocker de React Router: interceptar navegación interna y mostrar confirm()
```

**Nota:** `useBlocker` requiere `createBrowserRouter` (data router). La app usa `BrowserRouter` — esto causó un crash que fue corregido en hotfix2.

### Fix Docker adicional
```
Vite no detecta cambios en el volumen Docker en Windows (inotify no propaga
eventos cross-OS). Fix: agregar polling en vite.config.js:
server.watch.usePolling = true, interval = 500
```

## Resultado
- Preview de severidad en tiempo real en RiskForm
- Edición inline de usuarios en AdminPage
- Indicador + useBeforeUnload en MitigationPlanPanel
- Vite con polling habilitado para Docker en Windows
