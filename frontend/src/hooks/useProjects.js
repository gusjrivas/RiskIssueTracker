import { useState, useEffect, useCallback } from 'react'
import * as projectsApi from '../api/projects'

export function useProjects() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await projectsApi.getProjects()
      setData(res.items)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const createProject = useCallback(async (data) => {
    const project = await projectsApi.createProject(data)
    setData(prev => [project, ...prev])
    return project
  }, [])

  return { data, loading, error, refetch: load, createProject }
}
