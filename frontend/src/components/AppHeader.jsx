import { Link } from 'react-router-dom'
import { BarChart3, ShieldCheck, UserCircle } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export default function AppHeader() {
  const { user, logout } = useAuth()

  return (
    <header className="border-b border-border bg-surface">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="font-display text-xl font-bold">RiskTracker</Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted">{user?.full_name}</span>
          <Link to="/dashboard" className="flex items-center gap-1.5 text-sm text-muted hover:text-ink transition-colors">
            <BarChart3 size={15} strokeWidth={1.5} />
            Dashboard
          </Link>
          {user?.role === 'admin' && (
            <Link to="/admin" className="flex items-center gap-1.5 text-sm text-muted hover:text-ink transition-colors">
              <ShieldCheck size={15} strokeWidth={1.5} />
              Administración
            </Link>
          )}
          <Link to="/profile" className="flex items-center gap-1.5 text-sm text-muted hover:text-ink transition-colors">
            <UserCircle size={15} strokeWidth={1.5} />
            Mi Perfil
          </Link>
          <button onClick={logout} className="text-sm text-muted hover:text-ink transition-colors">
            Salir
          </button>
        </div>
      </div>
    </header>
  )
}
