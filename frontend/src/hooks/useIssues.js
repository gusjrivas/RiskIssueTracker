import { useState, useEffect, useCallback } from 'react'
import * as issuesApi from '../api/issues'

export function useIssues(params = {}) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await issuesApi.getIssues(params)
      setData(res.items)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(params)])

  useEffect(() => { load() }, [load])

  const createIssue = useCallback(async (payload) => {
    const issue = await issuesApi.createIssue(payload)
    setData(prev => [issue, ...prev])
    return issue
  }, [])

  const updateIssue = useCallback(async (id, payload) => {
    const updated = await issuesApi.updateIssue(id, payload)
    setData(prev => prev.map(i => i.id === id ? updated : i))
    return updated
  }, [])

  const deleteIssue = useCallback(async (id) => {
    await issuesApi.deleteIssue(id)
    setData(prev => prev.filter(i => i.id !== id))
  }, [])

  const transition = useCallback(async (id, status) => {
    const updated = await issuesApi.transitionIssueStatus(id, status)
    setData(prev => prev.map(i => i.id === id ? updated : i))
    return updated
  }, [])

  return { data, loading, error, refetch: load, createIssue, updateIssue, deleteIssue, transition }
}
