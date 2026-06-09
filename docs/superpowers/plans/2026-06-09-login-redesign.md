# Login Page Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar el layout actual de LoginPage (panel centrado) por un split screen con panel izquierdo oscuro (branding) y panel derecho blanco (formulario), manteniendo toda la lógica existente intacta.

**Architecture:** Solo se modifica la capa de presentación de `LoginPage.jsx`. La lógica de auth (handleSubmit, handleGoogleResponse, renderGoogleButton, efectos) no se toca. Se agrega una clase CSS helper en `index.css` para el detalle decorativo del panel izquierdo.

**Tech Stack:** React, Tailwind CSS, framer-motion (ya instalados), variables CSS existentes (`--ink`, `--canvas`, `--muted`, `--border`, `--surface`), color `#DC2626` (ya disponible como `severity-red`).

---

## Mapa de archivos

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `frontend/src/pages/LoginPage.jsx` | Modificar | Reemplazar JSX de presentación con layout split screen |
| `frontend/src/index.css` | Modificar | Agregar clase `.login-accent-bar` para la línea roja inferior del panel izquierdo |

---

### Task 1: Agregar clase CSS helper en index.css

**Files:**
- Modify: `frontend/src/index.css`

- [ ] **Step 1: Abrir `frontend/src/index.css` y agregar la clase al final del `@layer components`**

Ubicar el bloque `@layer components { ... }` (termina en la línea con `.card { ... }`). Agregar antes del cierre `}`:

```css
  .login-accent-bar {
    @apply absolute bottom-0 left-0 right-0 h-[3px] bg-[#DC2626];
  }
```

El bloque completo al final del layer debe quedar:

```css
  .card {
    @apply bg-surface border border-border p-6;
  }

  .login-accent-bar {
    @apply absolute bottom-0 left-0 right-0 h-[3px] bg-[#DC2626];
  }
}
```

- [ ] **Step 2: Verificar que no hay errores de sintaxis**

Abrir el archivo y confirmar que el `@layer components` tiene exactamente un `}` de cierre al final y que `.login-accent-bar` está dentro.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/index.css
git commit -m "style: add login-accent-bar helper class"
```

---

### Task 2: Refactorizar el JSX de presentación de LoginPage

**Files:**
- Modify: `frontend/src/pages/LoginPage.jsx`

La lógica (imports de hooks, estados, handlers, efectos) no cambia. Solo se reemplaza el JSX retornado por cada rama del componente.

- [ ] **Step 1: Reemplazar el bloque `if (blocked)` con layout split screen**

Localizar (línea ~106):
```jsx
  if (blocked) {
    const isPending = blocked.toLowerCase().includes('pendiente')
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
        <div className="card max-w-sm w-full text-center space-y-3">
          ...
        </div>
      </div>
    )
  }
```

Reemplazar con:
```jsx
  if (blocked) {
    const isPending = blocked.toLowerCase().includes('pendiente')
    return (
      <div className="min-h-screen flex flex-col md:flex-row">
        <LeftPanel />
        <div className="flex-1 bg-surface flex items-center justify-center p-8">
          <div className="w-full max-w-sm text-center space-y-4">
            <h2 className="font-display text-xl font-bold text-ink">
              {isPending ? 'Cuenta pendiente' : 'Cuenta desactivada'}
            </h2>
            <p className="text-sm text-muted">{blocked}</p>
            <button onClick={() => setBlocked(null)} className="btn-secondary w-full">
              Volver al login
            </button>
          </div>
        </div>
      </div>
    )
  }
```

- [ ] **Step 2: Reemplazar el bloque `if (registered)` con layout split screen**

Localizar (línea ~123):
```jsx
  if (registered) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
        <div className="card max-w-sm w-full text-center space-y-3">
          ...
        </div>
      </div>
    )
  }
```

Reemplazar con:
```jsx
  if (registered) {
    return (
      <div className="min-h-screen flex flex-col md:flex-row">
        <LeftPanel />
        <div className="flex-1 bg-surface flex items-center justify-center p-8">
          <div className="w-full max-w-sm text-center space-y-4">
            <h2 className="font-display text-xl font-bold text-ink">Cuenta creada</h2>
            <p className="text-sm text-muted">Tu cuenta está pendiente de aprobación por un administrador.</p>
            <button onClick={() => { setMode('login'); setRegistered(false) }} className="btn-secondary w-full">
              Volver al login
            </button>
          </div>
        </div>
      </div>
    )
  }
```

- [ ] **Step 3: Reemplazar el return principal con layout split screen**

Localizar (línea ~137):
```jsx
  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="w-full max-w-sm"
      >
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-ink">RiskTracker</h1>
          <p className="text-muted text-sm mt-1">Gestión de riesgos e issues</p>
        </div>

        <div className="card space-y-5">
          <div className="flex border border-border">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'login' ? 'bg-ink text-canvas' : 'text-ink hover:opacity-80'}`}
            >
              Ingresar
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'register' ? 'bg-ink text-canvas' : 'text-ink hover:opacity-80'}`}
            >
              Registrarse
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            {mode === 'register' && (
              <input
                value={form.full_name}
                onChange={set('full_name')}
                required
                placeholder="Nombre completo"
                className="input"
              />
            )}
            <input
              type="email"
              value={form.email}
              onChange={set('email')}
              required
              placeholder="Email"
              className="input"
            />
            <input
              type="password"
              value={form.password}
              onChange={set('password')}
              required
              placeholder="Contraseña"
              className="input"
            />
            {error && <p className="text-xs text-severity-red">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading && <Loader2 size={14} className="animate-spin" />}
              {mode === 'login' ? 'Ingresar' : 'Crear cuenta'}
            </button>
          </form>

          {GOOGLE_CLIENT_ID && (
            <>
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-surface text-muted">o continuá con</span>
                </div>
              </div>
              <div id="google-signin-btn" className="w-full flex justify-center" />
            </>
          )}
        </div>
      </motion.div>
    </div>
  )
```

Reemplazar con:
```jsx
  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <LeftPanel />
      <div className="flex-1 bg-surface flex items-center justify-center p-8 md:p-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="w-full max-w-sm"
        >
          <div className="mb-6">
            <h2 className="font-display text-2xl font-bold text-ink">
              {mode === 'login' ? 'Bienvenido' : 'Crear cuenta'}
            </h2>
            <p className="text-muted text-xs mt-1">
              {mode === 'login' ? 'Ingresá a tu cuenta para continuar' : 'Completá los datos para registrarte'}
            </p>
          </div>

          <div className="flex border border-border mb-6">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'login' ? 'bg-ink text-canvas' : 'text-muted hover:opacity-80'}`}
            >
              Ingresar
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'register' ? 'bg-ink text-canvas' : 'text-muted hover:opacity-80'}`}
            >
              Registrarse
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div className="flex flex-col gap-1">
                <label className="text-[11px] font-semibold text-muted uppercase tracking-wide">Nombre completo</label>
                <input
                  value={form.full_name}
                  onChange={set('full_name')}
                  required
                  placeholder="Juan Pérez"
                  className="input focus:border-[#DC2626]"
                />
              </div>
            )}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-muted uppercase tracking-wide">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={set('email')}
                required
                placeholder="usuario@empresa.com"
                className="input focus:border-[#DC2626]"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-muted uppercase tracking-wide">Contraseña</label>
              <input
                type="password"
                value={form.password}
                onChange={set('password')}
                required
                placeholder="••••••••"
                className="input focus:border-[#DC2626]"
              />
            </div>
            {error && <p className="text-xs text-severity-red">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 mt-2">
              {loading && <Loader2 size={14} className="animate-spin" />}
              {mode === 'login' ? 'Ingresar' : 'Crear cuenta'}
            </button>
          </form>

          {GOOGLE_CLIENT_ID && (
            <>
              <div className="relative my-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-surface text-muted">o continuá con</span>
                </div>
              </div>
              <div id="google-signin-btn" className="w-full flex justify-center" />
            </>
          )}
        </motion.div>
      </div>
    </div>
  )
```

- [ ] **Step 4: Agregar el componente `LeftPanel` dentro del mismo archivo, antes del `export default`**

Agregar estas líneas justo antes de `export default function LoginPage()`:

```jsx
function LeftPanel() {
  return (
    <div className="relative flex-1 bg-[#0A0A0A] flex flex-col items-center justify-center p-12 min-h-[200px] md:min-h-screen">
      <div
        className="flex items-center justify-center mb-5 rounded-[16px]"
        style={{
          width: 72,
          height: 72,
          background: '#DC2626',
          boxShadow: '0 8px 32px rgba(220,38,38,0.35)',
        }}
      >
        <span className="font-display font-black text-white text-4xl leading-none">R</span>
      </div>
      <div className="font-display font-bold text-[#F0F0EE] uppercase tracking-[2.5px] text-lg mb-3">
        RiskTracker
      </div>
      <div className="w-10 h-[2px] bg-[#DC2626] mb-4" />
      <p className="text-[#6B7280] text-xs italic text-center leading-relaxed max-w-[180px]">
        "Identificá riesgos antes de que se conviertan en problemas"
      </p>
      <div className="login-accent-bar" />
    </div>
  )
}
```

- [ ] **Step 5: Verificar el archivo final completo**

El archivo `LoginPage.jsx` debe tener esta estructura general (lógica intacta, solo JSX cambiado):

```
imports (sin cambios)

const GOOGLE_CLIENT_ID = ...

function LeftPanel() { ... }   ← NUEVO

export default function LoginPage() {
  // estados (sin cambios)
  // handlers (sin cambios)
  // efectos (sin cambios)

  if (blocked) { return <div ... ><LeftPanel /><div ...>...</div></div> }
  if (registered) { return <div ... ><LeftPanel /><div ...>...</div></div> }

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <LeftPanel />
      <div ...>
        <motion.div ...>
          ... formulario ...
        </motion.div>
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/LoginPage.jsx
git commit -m "feat: redesign login page with split screen layout"
```

---

### Task 3: Verificación visual

**Files:**
- No se modifican archivos

- [ ] **Step 1: Levantar el frontend**

```bash
cd frontend
npm run dev
```

Abrir `http://localhost:5173` en el navegador.

- [ ] **Step 2: Verificar modo "Ingresar"**

Checklist visual:
- [ ] Panel izquierdo negro ocupa mitad de la pantalla
- [ ] Ícono "R" rojo cuadrado con sombra visible
- [ ] Texto "RISKTRACKER" en blanco mayúscula
- [ ] Separador rojo fino
- [ ] Tagline en gris itálico
- [ ] Línea roja de 3px pegada al borde inferior del panel izquierdo
- [ ] Panel derecho blanco con formulario
- [ ] Labels visibles sobre cada campo ("EMAIL", "CONTRASEÑA")
- [ ] Título "Bienvenido" y subtítulo visibles
- [ ] Tabs "Ingresar / Registrarse" funcionales
- [ ] Botón "Ingresar" en negro, ancho completo

- [ ] **Step 3: Verificar modo "Registrarse"**

Hacer clic en tab "Registrarse":
- [ ] Aparece el campo "NOMBRE COMPLETO" con label
- [ ] El título cambia a "Crear cuenta"
- [ ] El subtítulo cambia a "Completá los datos para registrarte"
- [ ] El botón dice "Crear cuenta"

- [ ] **Step 4: Verificar mobile (< 768px)**

Reducir ventana a menos de 768px:
- [ ] Los paneles se apilan verticalmente
- [ ] El panel izquierdo queda arriba como franja compacta (`min-h-[200px]`)
- [ ] El formulario queda debajo

- [ ] **Step 5: Verificar estados especiales**

Para probar el estado "Cuenta pendiente" temporalmente, en `LoginPage.jsx` agregar `setBlocked('Tu cuenta está pendiente de aprobación.')` en el `useEffect` inicial (solo para test, revertir después):
- [ ] Aparece layout split screen con mensaje centrado en panel derecho
- [ ] Botón "Volver al login" funciona
- [ ] Revertir el cambio de test

- [ ] **Step 6: Commit final si todo está OK**

```bash
git add -p
git commit -m "chore: verify login redesign complete"
```
