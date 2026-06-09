import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

function LeftPanel() {
  return (
    <div className="relative flex-1 bg-[#0A0A0A] flex flex-col items-center justify-center p-12 min-h-[200px] md:min-h-screen">
      <div
        className="flex items-center justify-center mb-5 rounded-[16px]"
        style={{
          width: 72,
          height: 72,
          background: '#DC2626',
          boxShadow: '0 8px 32px rgba(220,38,38,0.35)',
        }}
      >
        <span className="font-display font-black text-white text-4xl leading-none">R</span>
      </div>
      <div className="font-display font-bold text-white uppercase tracking-[2.5px] text-lg mb-3">
        RiskTracker
      </div>
      <div className="w-10 h-[2px] bg-severity-red mb-4" />
      <p className="text-muted text-xs italic text-center leading-relaxed max-w-[180px]">
        "Identificá riesgos antes de que se conviertan en problemas"
      </p>
      <div className="login-accent-bar" />
    </div>
  )
}

export default function LoginPage() {
  const { loginWithPassword, loginWithGoogle, register } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [registered, setRegistered] = useState(false)
  const [blocked, setBlocked] = useState(null)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const isAccessBlocked = (msg) =>
    msg?.toLowerCase().includes('pendiente') || msg?.toLowerCase().includes('desactivada')

  const handleGoogleResponse = useCallback(async (response) => {
    setError(null)
    setLoading(true)
    try {
      await loginWithGoogle(response.credential)
      navigate('/')
    } catch (err) {
      if (isAccessBlocked(err.message)) {
        setBlocked(err.message)
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }, [loginWithGoogle, navigate])

  const renderGoogleButton = useCallback(() => {
    if (!GOOGLE_CLIENT_ID || !window.google?.accounts?.id) return
    const btn = document.getElementById('google-signin-btn')
    if (btn) {
      btn.innerHTML = ''
      window.google.accounts.id.renderButton(btn, {
        theme: 'outline',
        size: 'large',
        width: btn.offsetWidth || 320,
        text: 'signin_with',
        locale: 'es',
      })
    }
  }, [])

  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return
    if (window.google?.accounts?.id) {
      renderGoogleButton()
      return
    }
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.onload = () => {
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
      })
      renderGoogleButton()
    }
    document.head.appendChild(script)
    return () => { if (document.head.contains(script)) document.head.removeChild(script) }
  }, [handleGoogleResponse, renderGoogleButton])

  // Re-render button when mode changes (div gets remounted)
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return
    const timer = setTimeout(renderGoogleButton, 50)
    return () => clearTimeout(timer)
  }, [mode, renderGoogleButton])

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
      if (isAccessBlocked(err.message)) {
        setBlocked(err.message)
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  if (blocked) {
    const isPending = blocked.toLowerCase().includes('pendiente')
    return (
      <div className="min-h-screen flex flex-col md:flex-row">
        <LeftPanel />
        <div className="flex-1 bg-surface flex items-center justify-center p-8">
          <div className="w-full max-w-sm text-center space-y-4">
            <h2 className="font-display text-xl font-bold text-ink">
              {isPending ? 'Cuenta pendiente' : 'Cuenta desactivada'}
            </h2>
            <p className="text-sm text-muted">{blocked}</p>
            <button onClick={() => setBlocked(null)} className="btn-secondary w-full">
              Volver al login
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (registered) {
    return (
      <div className="min-h-screen flex flex-col md:flex-row">
        <LeftPanel />
        <div className="flex-1 bg-surface flex items-center justify-center p-8">
          <div className="w-full max-w-sm text-center space-y-4">
            <h2 className="font-display text-xl font-bold text-ink">Cuenta creada</h2>
            <p className="text-sm text-muted">Tu cuenta está pendiente de aprobación por un administrador.</p>
            <button onClick={() => { setMode('login'); setRegistered(false) }} className="btn-secondary w-full">
              Volver al login
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      <LeftPanel />
      <div className="login-right-panel flex-1 bg-surface flex items-center justify-center p-8 md:p-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          className="w-full max-w-sm"
        >
          <div className="mb-6">
            <h2 className="font-display text-2xl font-bold text-ink">
              {mode === 'login' ? 'Bienvenido' : 'Crear cuenta'}
            </h2>
            <p className="text-muted text-xs mt-1">
              {mode === 'login' ? 'Ingresá a tu cuenta para continuar' : 'Completá los datos para registrarte'}
            </p>
          </div>

          <div className="flex border border-border mb-6">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'login' ? 'bg-ink text-canvas' : 'text-muted hover:opacity-80'}`}
            >
              Ingresar
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 py-2 text-sm font-medium transition-colors ${mode === 'register' ? 'bg-ink text-canvas' : 'text-muted hover:opacity-80'}`}
            >
              Registrarse
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div className="flex flex-col gap-1">
                <label className="text-[11px] font-semibold text-muted uppercase tracking-wide">Nombre completo</label>
                <input
                  value={form.full_name}
                  onChange={set('full_name')}
                  required
                  placeholder="Juan Pérez"
                  className="input"
                />
              </div>
            )}
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-muted uppercase tracking-wide">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={set('email')}
                required
                placeholder="usuario@empresa.com"
                className="input"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-[11px] font-semibold text-muted uppercase tracking-wide">Contraseña</label>
              <input
                type="password"
                value={form.password}
                onChange={set('password')}
                required
                placeholder="••••••••"
                className="input"
              />
            </div>
            {error && <p className="text-xs text-severity-red">{error}</p>}
            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2 mt-2">
              {loading && <Loader2 size={14} className="animate-spin" />}
              {mode === 'login' ? 'Ingresar' : 'Crear cuenta'}
            </button>
          </form>

          {GOOGLE_CLIENT_ID && (
            <>
              <div className="relative my-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-surface text-muted">o continuá con</span>
                </div>
              </div>
              <div id="google-signin-btn" className="w-full flex justify-center" />
            </>
          )}
        </motion.div>
      </div>
    </div>
  )
}

