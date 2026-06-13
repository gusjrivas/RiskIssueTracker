import { useState, useRef, useCallback } from 'react'
import * as dashboardApi from '../api/dashboard'

// Hook con cache en memoria por clave `severity-type`, para que cada celda de
// la matriz de severidad pueda pedir sus riesgos/issues sin re-fetchear si
// ya se cargaron antes.
export function useSeverityItems() {
  const [itemsByKey, setItemsByKey] = useState({})
  const [loadingByKey, setLoadingByKey] = useState({})
  const [errorByKey, setErrorByKey] = useState({})
  const cache = useRef({})

  const fetchItems = useCallback(async (severity, type) => {
    const key = `${severity}-${type}`
    if (cache.current[key]) return

    setLoadingByKey(prev => ({ ...prev, [key]: true }))
    try {
      const res = await dashboardApi.getSeverityItems(severity, type)
      cache.current[key] = res.items
      setItemsByKey(prev => ({ ...prev, [key]: res.items }))
      setErrorByKey(prev => ({ ...prev, [key]: null }))
    } catch (e) {
      setErrorByKey(prev => ({ ...prev, [key]: e.message }))
    } finally {
      setLoadingByKey(prev => ({ ...prev, [key]: false }))
    }
  }, [])

  return { itemsByKey, loadingByKey, errorByKey, fetchItems }
}
