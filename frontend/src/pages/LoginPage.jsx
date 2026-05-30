import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { loginWithPassword, register } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [registered, setRegistered] = useState(false)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (mode === 'login') {
        await loginWithPassword(form.email, form.password)
        navigate('/')
      } else {
        await register(form.email, form.password, form.full_name)
        setRegistered(true)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (registered) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
        <div className="card max-w-sm w-full text-center space-y-3">
          <h2 className="font-display text-xl font-bold">Cuenta creada</h2>
          <p className="text-sm text-muted">Tu cuenta está pendiente de aprobación por un administrador.</p>
          <button onClick={() => { setMode('login'); setRegistered(false) }} className="btn-secondary w-full">
            Volver al login
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="w-full max-w-sm"
      >
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-ink">RiskTracker</h1>
          <p className="text-muted text-sm mt-1">Gestión de riesgos e issues</p>
        </div>

        <div className="card space-y-5">
          <div className="flex border border-border">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'login' ? 'bg-ink text-canvas' : 'text-muted hover:text-ink'}`}
            >
              Ingresar
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'register' ? 'bg-ink text-canvas' : 'text-muted hover:text-ink'}`}
            >
              Registrarse
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            {mode === 'register' && (
              <input
                value={form.full_name}
                onChange={set('full_name')}
                required
                placeholder="Nombre completo"
                className="input"
              />
            )}
            <input
              type="email"
              value={form.email}
              onChange={set('email')}
              required
              placeholder="Email"
              className="input"
            />
            <input
              type="password"
              value={form.password}
              onChange={set('password')}
              required
              placeholder="Contraseña"
              className="input"
            />
            {error && <p className="text-xs text-severity-red">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading && <Loader2 size={14} className="animate-spin" />}
              {mode === 'login' ? 'Ingresar' : 'Crear cuenta'}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  )
}
