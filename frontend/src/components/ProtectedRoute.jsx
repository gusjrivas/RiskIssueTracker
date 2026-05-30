import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-ink border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />

  if (user.status === 'pending') {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center">
        <div className="card max-w-md text-center space-y-3">
          <h2 className="font-display text-xl font-bold">Cuenta pendiente</h2>
          <p className="text-muted text-sm">Tu cuenta está siendo revisada por un administrador. Te notificaremos cuando sea aprobada.</p>
        </div>
      </div>
    )
  }

  if (user.status === 'inactive') {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center">
        <div className="card max-w-md text-center space-y-3">
          <h2 className="font-display text-xl font-bold">Cuenta desactivada</h2>
          <p className="text-muted text-sm">Tu cuenta ha sido desactivada. Contactá al administrador para más información.</p>
        </div>
      </div>
    )
  }

  return children
}
