import { useState, useCallback } from 'react'
import * as risksApi from '../api/risks'
import * as issuesApi from '../api/issues'

export function useMitigationPlan(entityType, entityId) {
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const save = useCallback(async (data) => {
    setSaving(true)
    setError(null)
    try {
      if (entityType === 'risk') return await risksApi.updateRisk(entityId, data)
      return await issuesApi.updateIssue(entityId, data)
    } catch (e) {
      setError(e.message)
      throw e
    } finally {
      setSaving(false)
    }
  }, [entityType, entityId])

  return { saving, error, save }
}
