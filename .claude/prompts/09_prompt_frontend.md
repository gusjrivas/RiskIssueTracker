# Prompt 09 — Frontend completo (SPA React)

## Contexto
Implementación completa del frontend como SPA con React, siguiendo el sistema de diseño minimalista definido en los skills del proyecto.

## Prompts

### Iniciar rama y desarrollo
```
arranquemos con el frontend armemos un branch para ese desarrollo
arranquemos con el frontend
```

### Diseño y arquitectura
```
Implementá el frontend completo siguiendo estas convenciones:

Sistema de diseño (minimalista moderno):
- Fuentes: Syne (display/títulos) + DM Sans (cuerpo)
- Paleta: canvas #F5F5F3, ink #0A0A0A, muted #6B7280, border #E5E5E3
- Accent: #3B5BDB (azul), severity: red #DC2626, yellow #D97706, green #16A34A
- Sin glassmorphism, sin gradientes fuertes, sin purple accent

Arquitectura (reglas estrictas):
- pages/ — vistas completas, una por ruta. No hacen fetch directo.
- components/ — reutilizables, reciben props, sin llamadas HTTP
- hooks/ — encapsulan api/ + estado (loading/error/data)
- api/ — funciones puras HTTP, solo llaman a client.js

Rutas:
- /login — login y registro
- / — Dashboard con grilla de proyectos
- /projects/:projectId/risks — lista de riesgos del proyecto
- /risks/:riskId — detalle de riesgo
- /issues/:issueId — detalle de issue
```

### Componentes requeridos
```
Implementá los siguientes componentes:

SeverityBadge: 
- Severidad 1-3 → clase severity-red
- Severidad 4-6 → clase severity-yellow  
- Severidad 7-9 → severity-green
- Con data-testid="severity-badge"

StatusBadge:
- open → "Abierto" (accent azul)
- in_progress → "En progreso" (amarillo)
- closed → "Cerrado" (verde)
- derived → "Derivado" (muted)
- pending → "Pendiente" (amarillo)
- active → "Activo" (verde)
- inactive → "Inactivo" (rojo)
- Con data-testid="status-badge"

ProtectedRoute:
- spinner → redirect /login si no hay usuario
- pantalla "cuenta pendiente" si status=pending
- pantalla "cuenta desactivada" si status=inactive
- render children si todo ok

StatusTransitionButton: botón que muestra la próxima acción según el estado actual
HistoryTimeline: timeline de transiciones con dot design
MitigationPlanPanel: dual textarea para mitigation + contingency con auto-save
RiskCard: tarjeta con severidad, estado, categoría. Link a /risks/:id
RiskForm: formulario completo con todos los campos del dominio
```

### Auth hook
```
Implementá useAuth como Context + Provider:
- AuthProvider wrappea toda la app en main.jsx
- useEffect al montar: si hay token en localStorage, hace GET /me para rehidratar el usuario
- loginWithPassword: POST /auth/login → guarda token → GET /me → setUser
- loginWithGoogle: POST /auth/google → igual que password
- register: POST /auth/register (no hace login automático)
- logout: limpia token + setUser(null)

IMPORTANTE: el archivo debe ser useAuth.jsx (no .js) porque tiene JSX en el Provider
```

### Tests frontend
```
Escribí tests con Vitest para:
- StatusBadge: todos los estados con sus textos y clases CSS
- SeverityBadge: rangos 1-3, 4-6, 7-9 con clases correctas

Los tests deben usar data-testid para seleccionar los elementos.
```

## Branch
`feat/frontend`

## Resultado
- SPA completa con todas las vistas funcionando
- 10 tests de StatusBadge pasando
- Sistema de diseño implementado con Tailwind
- Hot reload via Vite
