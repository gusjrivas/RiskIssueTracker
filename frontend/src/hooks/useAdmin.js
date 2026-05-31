import { useState, useEffect, useCallback } from 'react'
import { getUsers, approveUser, deactivateUser, updateUser as updateUserApi } from '../api/admin'

export function useAdmin() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(() => {
    setLoading(true)
    getUsers()
      .then(res => setData(res.items))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const approve = useCallback(async (userId) => {
    const updated = await approveUser(userId)
    setData(prev => prev.map(u => u.id === updated.id ? updated : u))
  }, [])

  const deactivate = useCallback(async (userId) => {
    const updated = await deactivateUser(userId)
    setData(prev => prev.map(u => u.id === updated.id ? updated : u))
  }, [])

  const updateUser = useCallback(async (userId, body) => {
    const updated = await updateUserApi(userId, body)
    setData(prev => prev.map(u => u.id === updated.id ? updated : u))
  }, [])

  return { data, loading, error, approve, deactivate, updateUser, refetch: fetch }
}
