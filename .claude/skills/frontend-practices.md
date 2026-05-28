# Skill: Frontend Best Practices

---

## Estructura de capas

```
pages/   → usan hooks, pasan props a components — sin fetch directo
hooks/   → llaman api/, manejan loading/error/data + mutaciones
api/     → funciones puras HTTP usando client.js
components/ → reciben props, renderizan UI — sin llamadas HTTP
```

---

## Patrón de hook estándar

```js
// hooks/useRisks.js
import { useState, useEffect } from 'react'
import { getRisks } from '../api/risks'

export function useRisks(projectId) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    getRisks(projectId)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [projectId])

  return { data, loading, error }
}
```

## Patrón de hook con mutación

```js
export function useRisks(projectId) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = useCallback(() => { ... }, [projectId])

  const create = async (payload) => {
    const newRisk = await createRisk(payload)
    setData(prev => [...prev, newRisk])
    return newRisk
  }

  useEffect(() => { refresh() }, [refresh])

  return { data, loading, error, create, refresh }
}
```

---

## Auth

### AuthContext

```js
// Provee: { user, token, login, logout, loading }
// Leer siempre desde useAuth() — nunca leer localStorage directamente en componentes
```

### Token en requests

`client.js` lee el token del localStorage y lo agrega al header `Authorization: Bearer {token}` automáticamente en cada request autenticado.

### ProtectedRoute

Envolver todas las rutas privadas:
```jsx
<Route path="/risks" element={
  <ProtectedRoute>
    <RisksPage />
  </ProtectedRoute>
} />
```

`ProtectedRoute` redirige a `/login` si no hay token, o muestra pantalla de "Pendiente de aprobación" si `user.status === 'pending'`.

---

## Paginación

Los hooks que listan recursos manejan `page` y `size`:

```js
const [page, setPage] = useState(1)
const { data, loading } = useRisks({ projectId, page, size: 20 })
// data = { items: [], total: N, page: N, size: N, pages: N }
```

---

## Manejo de errores en UI

- Mostrar siempre un estado de error visible al usuario (no solo `console.error`)
- Los componentes reciben `error` como prop y deciden cómo renderizarlo
- Errores 401 → redirigir a login (en `client.js`)
- Errores 403 → mostrar mensaje "Sin permisos"
- Errores 409 → mostrar mensaje específico del `detail` del error

---

## SeverityBadge y StatusBadge

Son la **única fuente de verdad** para colores y etiquetas.
La severidad ahora es un número 1–9:

```jsx
// SeverityBadge recibe severity: number (1-9)
// Mapeo interno:
// 1-3 → rojo (crítico)
// 4-6 → amarillo (medio)
// 7-9 → verde (bajo)
```

Ningún otro componente hardcodea colores de severidad o estado.

---

## Google Sign-In

```jsx
import { GoogleLogin } from '@react-oauth/google'

<GoogleLogin
  onSuccess={({ credential }) => auth.loginWithGoogle(credential)}
  onError={() => setError('Error al iniciar sesión con Google')}
/>
```

El `credential` es el `id_token` que se envía al backend en `POST /auth/google`.
