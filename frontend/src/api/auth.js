import { apiGet, apiPost } from './client'

export const loginWithPassword = (email, password) =>
  apiPost('/api/v1/auth/login', { email, password })

export const loginWithGoogle = (id_token) =>
  apiPost('/api/v1/auth/google', { id_token })

export const register = (email, password, full_name) =>
  apiPost('/api/v1/auth/register', { email, password, full_name })

export const getMe = () => apiGet('/api/v1/auth/me')
