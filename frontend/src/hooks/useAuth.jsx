import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { setLoading(false); return }
    authApi.getMe()
      .then(setUser)
      .catch(() => localStorage.removeItem('access_token'))
      .finally(() => setLoading(false))
  }, [])

  const saveToken = (token) => localStorage.setItem('access_token', token)

  const loginWithPassword = useCallback(async (email, password) => {
    const res = await authApi.loginWithPassword(email, password)
    saveToken(res.access_token)
    const me = await authApi.getMe()
    setUser(me)
    return me
  }, [])

  const loginWithGoogle = useCallback(async (id_token) => {
    const res = await authApi.loginWithGoogle(id_token)
    saveToken(res.access_token)
    const me = await authApi.getMe()
    setUser(me)
    return me
  }, [])

  const register = useCallback((email, password, full_name) =>
    authApi.register(email, password, full_name), [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, loginWithPassword, loginWithGoogle, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
