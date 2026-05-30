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

export default function StatusTransitionButton({ currentStatus, onTransition, extraActions = [] }) {
  const [loading, setLoading] = useState(false)

  const next = NEXT_STATUS[currentStatus]
  if (!next && extraActions.length === 0) return null

  const handle = async (status) => {
    setLoading(true)
    try { await onTransition(status) }
    finally { setLoading(false) }
  }

  return (
    <div className="flex gap-2 flex-wrap">
      {next && (
        <button
          onClick={() => handle(next)}
          disabled={loading}
          className="btn-primary flex items-center gap-1.5"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <ArrowRight size={14} />}
          {LABELS[next] ?? next}
        </button>
      )}
      {extraActions.map(({ label, status }) => (
        <button
          key={status}
          onClick={() => handle(status)}
          disabled={loading}
          className="btn-secondary flex items-center gap-1.5"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <ArrowRight size={14} />}
          {label}
        </button>
      ))}
    </div>
  )
}
