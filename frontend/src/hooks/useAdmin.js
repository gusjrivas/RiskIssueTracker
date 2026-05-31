import { useState, useEffect, useCallback } from 'react'
import { getUsers, approveUser, deactivateUser } from '../api/admin'

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

  return { data, loading, error, approve, deactivate, refetch: fetch }
}
