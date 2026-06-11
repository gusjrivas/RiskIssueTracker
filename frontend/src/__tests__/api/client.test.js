import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { apiPost, apiGet } from '../../api/client'

function mockFetch(status, body) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText: `HTTP ${status}`,
    json: () => Promise.resolve(body),
  })
}

describe('client — manejo de 401', () => {
  let originalLocation

  beforeEach(() => {
    localStorage.clear()
    originalLocation = window.location
    // jsdom no permite asignar window.location.href sin esto
    delete window.location
    window.location = { href: '/' }
  })

  afterEach(() => {
    window.location = originalLocation
    vi.unstubAllGlobals()
  })

  it('un login fallido (401) lanza el error del backend en vez de redirigir', async () => {
    vi.stubGlobal('fetch', mockFetch(401, { detail: 'Credenciales inválidas' }))

    await expect(
      apiPost('/api/v1/auth/login', { email: 'a@b.com', password: 'wrong' })
    ).rejects.toThrow('Credenciales inválidas')

    expect(window.location.href).toBe('/')
  })

  it('un 401 en un endpoint protegido limpia el token y redirige a /login', async () => {
    localStorage.setItem('access_token', 'expired-token')
    vi.stubGlobal('fetch', mockFetch(401, { detail: 'Token inválido o expirado' }))

    await apiGet('/api/v1/risks')

    expect(localStorage.getItem('access_token')).toBeNull()
    expect(window.location.href).toBe('/login')
  })

  it('un 403 propaga el detalle del backend', async () => {
    vi.stubGlobal('fetch', mockFetch(403, { detail: 'Cuenta pendiente de aprobación' }))

    await expect(
      apiPost('/api/v1/auth/login', { email: 'a@b.com', password: 'x' })
    ).rejects.toThrow('Cuenta pendiente de aprobación')
  })
})
