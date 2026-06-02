import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ChevronLeft, Loader2, Sun, Moon, CheckCircle } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useProfile } from '../hooks/useProfile'

export default function ProfilePage() {
  const { user } = useAuth()
  const { loading, changePassword, changeTheme } = useProfile()

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState(null)
  const [passwordSuccess, setPasswordSuccess] = useState(false)

  const [themeError, setThemeError] = useState(null)

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setPasswordError(null)
    setPasswordSuccess(false)
    if (newPassword !== confirmPassword) {
      setPasswordError('Las contraseñas nuevas no coinciden')
      return
    }
    try {
      await changePassword(currentPassword, newPassword)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setPasswordSuccess(true)
    } catch (err) {
      setPasswordError(err.message)
    }
  }

  const handleThemeChange = async (theme) => {
    setThemeError(null)
    try {
      await changeTheme(theme)
    } catch (err) {
      setThemeError(err.message)
    }
  }

  const isGoogleOnly = user && !user.has_password

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border bg-surface">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/" className="flex items-center gap-1.5 text-sm text-muted hover:text-ink transition-colors">
            <ChevronLeft size={16} strokeWidth={1.5} />
            Proyectos
          </Link>
          <span className="text-border">|</span>
          <h1 className="font-display text-lg font-bold">Mi Perfil</h1>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-10 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="card space-y-1"
        >
          <p className="text-xs text-muted uppercase tracking-widest font-medium mb-3">Cuenta</p>
          <p className="font-display font-semibold text-lg">{user?.full_name}</p>
          <p className="text-sm text-muted">{user?.email}</p>
          <p className="text-xs text-muted capitalize">{user?.role === 'admin' ? 'Administrador' : 'Usuario'}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.05 }}
          className="card space-y-4"
        >
          <div>
            <p className="text-xs text-muted uppercase tracking-widest font-medium mb-1">Apariencia</p>
            <p className="text-sm text-muted">Elegí el tema de la interfaz</p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => handleThemeChange('light')}
              disabled={loading}
              className={`flex-1 flex items-center gap-3 border rounded-lg px-4 py-3 transition-colors ${
                user?.theme === 'light'
                  ? 'border-ink bg-canvas'
                  : 'border-border hover:border-ink/40'
              }`}
            >
              <Sun size={18} strokeWidth={1.5} className="text-muted shrink-0" />
              <div className="text-left">
                <p className="text-sm font-medium">Claro</p>
                <p className="text-xs text-muted">Fondo blanco</p>
              </div>
              {user?.theme === 'light' && (
                <CheckCircle size={16} className="ml-auto text-ink" strokeWidth={1.5} />
              )}
            </button>

            <button
              onClick={() => handleThemeChange('dark')}
              disabled={loading}
              className={`flex-1 flex items-center gap-3 border rounded-lg px-4 py-3 transition-colors ${
                user?.theme === 'dark'
                  ? 'border-ink bg-canvas'
                  : 'border-border hover:border-ink/40'
              }`}
            >
              <Moon size={18} strokeWidth={1.5} className="text-muted shrink-0" />
              <div className="text-left">
                <p className="text-sm font-medium">Oscuro</p>
                <p className="text-xs text-muted">Fondo oscuro</p>
              </div>
              {user?.theme === 'dark' && (
                <CheckCircle size={16} className="ml-auto text-ink" strokeWidth={1.5} />
              )}
            </button>
          </div>

          {themeError && (
            <p className="text-xs text-severity-red">{themeError}</p>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, delay: 0.1 }}
          className="card space-y-4"
        >
          <div>
            <p className="text-xs text-muted uppercase tracking-widest font-medium mb-1">Contraseña</p>
            {isGoogleOnly ? (
              <p className="text-sm text-muted">Tu cuenta usa autenticación de Google. No podés cambiar la contraseña aquí.</p>
            ) : (
              <p className="text-sm text-muted">Cambiá tu contraseña de acceso</p>
            )}
          </div>

          {!isGoogleOnly && (
            <form onSubmit={handlePasswordSubmit} className="space-y-3">
              <div>
                <label className="block text-xs text-muted mb-1">Contraseña actual</label>
                <input
                  type="password"
                  value={currentPassword}
                  onChange={e => setCurrentPassword(e.target.value)}
                  className="input"
                  required
                  autoComplete="current-password"
                />
              </div>
              <div>
                <label className="block text-xs text-muted mb-1">Nueva contraseña</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={e => setNewPassword(e.target.value)}
                  className="input"
                  required
                  minLength={8}
                  autoComplete="new-password"
                />
              </div>
              <div>
                <label className="block text-xs text-muted mb-1">Confirmar nueva contraseña</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  className="input"
                  required
                  autoComplete="new-password"
                />
              </div>

              {passwordError && (
                <p className="text-xs text-severity-red">{passwordError}</p>
              )}
              {passwordSuccess && (
                <p className="text-xs text-severity-green flex items-center gap-1.5">
                  <CheckCircle size={13} strokeWidth={1.5} />
                  Contraseña actualizada correctamente
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="btn-primary flex items-center gap-2"
              >
                {loading && <Loader2 size={14} className="animate-spin" />}
                Cambiar contraseña
              </button>
            </form>
          )}
        </motion.div>
      </main>
    </div>
  )
}
