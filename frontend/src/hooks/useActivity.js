import { useState, useEffect, useCallback } from 'react'
import { getRiskActivity, getIssueActivity } from '../api/activity'

export function useActivity(entityType, entityId) {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(() => {
    setLoading(true)
    const req = entityType === 'risk' ? getRiskActivity(entityId) : getIssueActivity(entityId)
    req
      .then(data => setEntries(data.items))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [entityType, entityId])

  useEffect(() => { fetch() }, [fetch])

  return { entries, loading, error, refresh: fetch }
}
