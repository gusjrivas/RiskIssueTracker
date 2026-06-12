import { useState } from 'react'
import { ArrowRight, Loader2 } from 'lucide-react'

const NEXT_STATUS = {
  open: 'in_progress',
  in_progress: 'closed',
}

const LABELS = {
  in_progress: 'Iniciar',
  closed: 'Cerrar',
  derived: 'Derivar a Issue',
}

const DISABLED_TITLE = 'Solo el creador, el responsable o un administrador pueden cambiar el estado'

export default function StatusTransitionButton({ currentStatus, onTransition, extraActions = [], disabled = false }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const next = NEXT_STATUS[currentStatus]
  if (!next && extraActions.length === 0) return null

  const handle = async (status) => {
    setLoading(true)
    setError(null)
    try {
      await onTransition(status)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const disabledCls = disabled ? 'opacity-50 cursor-not-allowed' : ''

  return (
    <div className="space-y-2">
      <div className="flex gap-2 flex-wrap">
        {next && (
          <button
            onClick={() => handle(next)}
            disabled={loading || disabled}
            title={disabled ? DISABLED_TITLE : undefined}
            className={`btn-primary flex items-center gap-1.5 ${disabledCls}`}
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <ArrowRight size={14} />}
            {LABELS[next] ?? next}
          </button>
        )}
        {extraActions.map(({ label, status }) => (
          <button
            key={status}
            onClick={() => handle(status)}
            disabled={loading || disabled}
            title={disabled ? DISABLED_TITLE : undefined}
            className={`btn-secondary flex items-center gap-1.5 ${disabledCls}`}
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <ArrowRight size={14} />}
            {label}
          </button>
        ))}
      </div>
      {error && <p className="text-xs text-severity-red">{error}</p>}
    </div>
  )
}
