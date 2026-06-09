# Prompt 23 — Feature: New Login Page

## Contexto
Desarrollar una interfaz UI para el login que sea mas amigable y agradable, respetando el look and feel de la aplicacion

## Branch
`feature/New-login-page`

## Requisito

Tener instalado superpowers. Si no lo tenemos, desde la consola de Claude, ejecutar:
/plugin install superpowers@claude-plugins-official

## Prompts

```
En la app de frontend, es necesario mejorar el look and feel de la pantalla de login. Podes tomar ideas de la siguiente web de login : https://www.sir360sr.com/arg/login.php
Sin embargo, tenes que respetar las rules existentes para la app frontend
```

## Resultado

Genero servidor local para mostrar propuestas. Por cada propuesta presentada en forma visual desde el servidor construido, pregunto por cual se prefiere teniendo 3 opciones disponibles.
Luego de elegir cada una, escribio un documento de especificacion, el cual se copia a continuacion. Por ultimo, luego de revisar dicho doc, se procedio a aprobarlo y a solicitar que lo implemente a traves de sub-agentes que fue orquestando hasta que el plan quedo completamente ejecutado y testeado.

## Documento de especificacion generado ( en /docs/superpowers/specs )

# Login Page Redesign — Spec

**Fecha:** 2026-06-09  
**Archivo a modificar:** `frontend/src/pages/LoginPage.jsx`  
**Archivos de soporte:** `frontend/src/index.css` (posiblemente `tailwind.config.js`)

---

## Objetivo

Mejorar el look & feel de la pantalla de login manteniendo toda la lógica existente (auth por email/password, Google OAuth, registro, estados de cuenta bloqueada/pendiente). Solo cambia la presentación visual.

---

## Layout

**Split screen de dos paneles**, ocupando toda la pantalla (`min-h-screen`):

- **Panel izquierdo** (50% del ancho): fondo negro `#0A0A0A`, contenido centrado verticalmente.
- **Panel derecho** (50% del ancho): fondo blanco `#FFFFFF`, formulario centrado verticalmente.
- En mobile (< `md`): los paneles se apilan verticalmente; el panel izquierdo colapsa a una franja compacta arriba y el formulario abajo.

---

## Panel izquierdo

Contenido centrado (`flex-col items-center justify-center`), de arriba hacia abajo:

1. **Ícono "R"** — caja cuadrada `72×72px`, `border-radius: 16px`, fondo `#DC2626`, letra "R" en blanco, `font-display`, `font-weight: 900`, `font-size: 32px`. Sombra: `box-shadow: 0 8px 32px rgba(220,38,38,0.35)`.
2. **Nombre** — `"RiskTracker"`, `font-display`, `font-weight: 700`, `letter-spacing: 2.5px`, `text-transform: uppercase`, color `#F0F0EE`, `font-size: 18px`. Margen superior: `20px`.
3. **Separador** — línea horizontal `40×2px`, color `#DC2626`. Margen: `12px` arriba y abajo.
4. **Tagline** — `"Identificá riesgos antes de que se conviertan en problemas"`, `font-style: italic`, `color: #6B7280`, `font-size: 12px`, `text-align: center`, `max-width: 180px`, `line-height: 1.6`.
5. **Detalle decorativo** — línea roja de `3px` de alto pegada al borde inferior del panel (`position: absolute; bottom: 0; left: 0; right: 0; background: #DC2626`).

---

## Panel derecho

Formulario centrado verticalmente con `padding: 48px 44px`.

### Encabezado del formulario
- Título: `"Bienvenido"` — `font-display`, `font-size: 22px`, `font-weight: 700`, color `#0A0A0A`.
- Subtítulo: `"Ingresá a tu cuenta para continuar"` (modo login) / `"Creá tu cuenta"` (modo registro) — `font-size: 12px`, `color: muted`.

### Tab switcher (Ingresar / Registrarse)
- Mismo componente existente (`border border-border`, dos botones `flex-1`), sin cambios funcionales.
- Activo: `bg-ink text-canvas`. Inactivo: `text-muted hover:opacity-80`.

### Campos del formulario
Cada campo tiene **label visible** encima del input (novedad respecto al diseño actual):
- Label: `font-size: 11px`, `font-weight: 600`, `color: muted`, `text-transform: uppercase`, `letter-spacing: 0.5px`.
- Input: clase `.input` existente, con override de focus para borde rojo: `focus:border-[#DC2626]`.
- Campos: igual que hoy (nombre completo solo en registro, email, password).

### Botón de submit
- Clase `.btn-primary` existente, ancho completo. Sin cambios funcionales.

### Divisor y botón Google
- Igual que hoy (solo visible si `GOOGLE_CLIENT_ID` está configurado).

---

## Estados especiales (bloqueado / registrado)

Las pantallas de "Cuenta pendiente" y "Cuenta creada" también adoptan el layout split screen, con el panel izquierdo idéntico y el mensaje en el panel derecho centrado.

---

## Restricciones / reglas respetadas

- **No se modifica lógica**: toda la lógica de auth, Google OAuth, navegación y manejo de errores permanece intacta.
- **Tokens CSS**: se usan las variables CSS existentes (`--ink`, `--canvas`, `--muted`, `--border`, `--surface`). El rojo `#DC2626` ya existe como `severity-red` en el sistema de colores.
- **Clases de componentes**: `.input`, `.btn-primary`, `.btn-secondary`, `.card` se reutilizan donde aplica.
- **Dark mode**: el panel derecho en dark mode usa `--surface` como fondo. El panel izquierdo es negro fijo (no cambia en dark).
- **Mobile**: breakpoint `md` de Tailwind (768px). Abajo de ese punto el layout es columna.
- **Fuentes**: `font-display` (Syne) para logo y título; `font-body` (DM Sans) para el resto — ambas ya cargadas.

---

## Archivos afectados

| Archivo | Cambio |
|---|---|
| `frontend/src/pages/LoginPage.jsx` | Refactor del JSX de presentación. Lógica intacta. |
| `frontend/src/index.css` | Posible clase helper `.login-left-accent` si se necesita el detalle decorativo inferior. |

---

## Lo que NO cambia

- Lógica de `handleSubmit`, `handleGoogleResponse`, `renderGoogleButton`, efectos de Google script.
- Manejo de estados: `mode`, `form`, `loading`, `error`, `registered`, `blocked`.
- Navegación post-login.
- Animación `framer-motion` de entrada (se conserva sobre el panel derecho).

