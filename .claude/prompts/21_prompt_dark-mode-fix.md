# Prompt 21 — Fix: dark mode CSS variables + botón Google OAuth (frontend)

## Contexto
Dos bugs visuales en modo oscuro y el botón de Google OAuth ausente en la pantalla de login.

## Branch
`fix/dark-mode-google-oauth`

## Prompts

```
no se ve el boton de Google OAuth en la pagina de login por eso no puedo ingresar con esa cuenta.
corregir el bug y volver a revisar el tema oscuro sigo viendo sin contraste el texto
en la solapa de riesgo/problema
```

```
el boton no aparece para registrarse con Google OAuth y hay un bug cuando se pasa de
ingresar a registrarse se pierde el botón para ingresar. corregir el bug
```

## Causa raíz — dark mode sin contraste

El `tailwind.config.js` tenía los colores **hardcodeados**:
```js
colors: { ink: '#0A0A0A', canvas: '#F5F5F3', ... }
```
Tailwind generaba `.text-ink { color: #0A0A0A }` (negro) que en modo oscuro
resultaba ilegible sobre el fondo `#1C1C1E`. Los overrides en `index.css` del tipo
`html.dark .text-ink { color: var(--ink) }` no alcanzaban a resolver todos los casos.

## Fix — CSS variables en Tailwind

```js
// tailwind.config.js
colors: {
  canvas: 'var(--canvas)',
  ink:    'var(--ink)',
  muted:  'var(--muted)',
  border: 'var(--border)',
  surface:'var(--surface)',
}
```

Con esto Tailwind genera `.text-ink { color: var(--ink) }` y el valor cambia
automáticamente entre `:root` (modo claro) y `html.dark` (modo oscuro).

También se reemplazó `hover:bg-border/50` → `hover:bg-border` en `.btn-secondary`
porque el modificador de opacidad `/N` no funciona con CSS variables.

## Fix — botón Google OAuth en LoginPage

Problema de re-renderizado: al cambiar entre Ingresar/Registrarse, el div
`#google-signin-btn` se desmontaba y el SDK de Google no re-renderizaba el botón solo.

```js
// GOOGLE_CLIENT_ID leído de import.meta.env.VITE_GOOGLE_CLIENT_ID
const renderGoogleButton = useCallback(() => {
  const btn = document.getElementById('google-signin-btn')
  if (btn) {
    btn.innerHTML = ''  // limpiar antes de re-renderizar
    window.google.accounts.id.renderButton(btn, { ... })
  }
}, [])

// Re-render al cambiar de modo
useEffect(() => {
  const timer = setTimeout(renderGoogleButton, 50)
  return () => clearTimeout(timer)
}, [mode, renderGoogleButton])
```

El botón se muestra en **ambos modos** (Ingresar y Registrarse) y persiste al cambiar de tab.

## Configuración Docker

```yaml
# docker-compose.yml — frontend
environment:
  VITE_API_URL: http://localhost:8000
  VITE_GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID:-}
```

## Resultado
- Todos los colores adaptan automáticamente entre modo claro y oscuro sin overrides manuales
- Solapas Riesgos/Issues y Login/Registro legibles en ambos modos
- Botón "Acceder con Google" visible en Ingresar y Registrarse, persiste al cambiar tab
- `GOOGLE_CLIENT_ID` en `.env` controla si el botón aparece (si está vacío, no se muestra)
