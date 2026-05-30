import { useState, useEffect, useCallback } from 'react'
import * as risksApi from '../api/risks'

export function useRisks(params = {}) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await risksApi.getRisks(params)
      setData(res.items)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(params)])

  useEffect(() => { load() }, [load])

  const createRisk = useCallback(async (payload) => {
    const risk = await risksApi.createRisk(payload)
    setData(prev => [risk, ...prev])
    return risk
  }, [])

  const updateRisk = useCallback(async (id, payload) => {
    const updated = await risksApi.updateRisk(id, payload)
    setData(prev => prev.map(r => r.id === id ? updated : r))
    return updated
  }, [])

  const deleteRisk = useCallback(async (id) => {
    await risksApi.deleteRisk(id)
    setData(prev => prev.filter(r => r.id !== id))
  }, [])

  const transition = useCallback(async (id, status) => {
    const updated = await risksApi.transitionRiskStatus(id, status)
    setData(prev => prev.map(r => r.id === id ? updated : r))
    return updated
  }, [])

  return { data, loading, error, refetch: load, createRisk, updateRisk, deleteRisk, transition }
}
