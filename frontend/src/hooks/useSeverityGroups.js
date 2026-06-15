import { useState, useCallback, useRef } from 'react'
import * as dashboardApi from '../api/dashboard'

// Hook lazy: no pide datos hasta que se llama fetchGroups() (al abrir la
// bandeja por primera vez), y luego cachea el resultado.
export function useSeverityGroups() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const fetched = useRef(false)

  const fetchGroups = useCallback(async () => {
    if (fetched.current) return
    fetched.current = true
    setLoading(true)
    try {
      const res = await dashboardApi.getSeverityGroups()
      setData(res.groups)
      setError(null)
    } catch (e) {
      setError(e.message)
      fetched.current = false
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, fetchGroups }
}
