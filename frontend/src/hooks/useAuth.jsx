import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

function applyTheme(theme) {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { setLoading(false); return }
    authApi.getMe()
      .then(me => { setUser(me); applyTheme(me.theme) })
      .catch(() => localStorage.removeItem('access_token'))
      .finally(() => setLoading(false))
  }, [])

  const saveToken = (token) => localStorage.setItem('access_token', token)

  const loginWithPassword = useCallback(async (email, password) => {
    const res = await authApi.loginWithPassword(email, password)
    saveToken(res.access_token)
    const me = await authApi.getMe()
    setUser(me)
    applyTheme(me.theme)
    return me
  }, [])

  const loginWithGoogle = useCallback(async (id_token) => {
    const res = await authApi.loginWithGoogle(id_token)
    saveToken(res.access_token)
    const me = await authApi.getMe()
    setUser(me)
    applyTheme(me.theme)
    return me
  }, [])

  const register = useCallback((email, password, full_name) =>
    authApi.register(email, password, full_name), [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    setUser(null)
    applyTheme('light')
  }, [])

  const refreshUser = useCallback(async () => {
    const me = await authApi.getMe()
    setUser(me)
    applyTheme(me.theme)
    return me
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, loginWithPassword, loginWithGoogle, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
