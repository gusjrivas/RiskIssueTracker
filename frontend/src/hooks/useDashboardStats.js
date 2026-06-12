import { useState, useEffect, useCallback } from 'react'
import * as dashboardApi from '../api/dashboard'

export function useDashboardStats() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await dashboardApi.getDashboardStats()
      setData(res)
      setError(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  return { data, loading, error, refetch: load }
}
