const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('access_token')
}

async function request(method, path, body) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const options = { method, headers }
  if (body !== undefined) {
    options.body = JSON.stringify(body)
  }

  const response = await fetch(`${BASE_URL}${path}`, options)

  // En los endpoints de ingreso un 401 significa credenciales inválidas:
  // hay que mostrar el error, no redirigir (eso perdería el mensaje).
  const isAuthEntry = path.startsWith('/api/v1/auth/login')
    || path.startsWith('/api/v1/auth/google')
    || path.startsWith('/api/v1/auth/register')

  if (response.status === 401 && !isAuthEntry) {
    localStorage.removeItem('access_token')
    window.location.href = '/login'
    return
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    const detail = error.detail
    const message = Array.isArray(detail)
      ? detail.map(e => e.msg || JSON.stringify(e)).join('; ')
      : detail || `HTTP ${response.status}`
    throw new Error(message)
  }

  if (response.status === 204) return null
  return response.json()
}

export const apiGet = (path) => request('GET', path)
export const apiPost = (path, body) => request('POST', path, body)
export const apiPatch = (path, body) => request('PATCH', path, body)
export const apiDelete = (path) => request('DELETE', path)
