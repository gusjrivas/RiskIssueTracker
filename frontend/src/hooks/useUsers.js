import { useState, useEffect } from 'react'
import { getActiveUsers } from '../api/users'

export function useUsers() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getActiveUsers()
      .then(data => setUsers(data.items))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return { users, loading, error }
}
