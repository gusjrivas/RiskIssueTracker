import { useState, useCallback } from 'react'
import * as authApi from '../api/auth'
import { useAuth } from './useAuth'

export function useProfile() {
  const { refreshUser } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const changePassword = useCallback(async (currentPassword, newPassword) => {
    setLoading(true)
    setError(null)
    try {
      await authApi.updatePassword(currentPassword, newPassword)
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const changeTheme = useCallback(async (theme) => {
    setLoading(true)
    setError(null)
    try {
      await authApi.updateTheme(theme)
      await refreshUser()
    } catch (err) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [refreshUser])

  return { loading, error, changePassword, changeTheme }
}
