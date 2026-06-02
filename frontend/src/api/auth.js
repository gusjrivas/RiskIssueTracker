import { apiGet, apiPost, apiPatch } from './client'

export const loginWithPassword = (email, password) =>
  apiPost('/api/v1/auth/login', { email, password })

export const loginWithGoogle = (id_token) =>
  apiPost('/api/v1/auth/google', { id_token })

export const register = (email, password, full_name) =>
  apiPost('/api/v1/auth/register', { email, password, full_name })

export const getMe = () => apiGet('/api/v1/auth/me')

export const updatePassword = (current_password, new_password) =>
  apiPatch('/api/v1/auth/me/password', { current_password, new_password })

export const updateTheme = (theme) =>
  apiPatch('/api/v1/auth/me/theme', { theme })
