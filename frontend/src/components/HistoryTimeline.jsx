import { useEffect, useState } from 'react'
import { Clock } from 'lucide-react'
import { apiGet } from '../api/client'

function formatDate(iso) {
  return new Date(iso).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' })
}

export default function HistoryTimeline({ entityType, entityId }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!entityId) return
    apiGet(`/api/v1/history/${entityType}/${entityId}`)
      .then(res => setItems(res.items))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [entityType, entityId])

  if (loading) return <div className="text-sm text-muted py-4">Cargando historial...</div>
  if (items.length === 0) return <div className="text-sm text-muted py-4">Sin transiciones registradas.</div>

  return (
    <div className="space-y-0">
      {items.map((entry, i) => (
        <div key={entry.id} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div className="w-2 h-2 rounded-full bg-ink mt-1.5 shrink-0" />
            {i < items.length - 1 && <div className="w-px flex-1 bg-border mt-1" />}
          </div>
          <div className="pb-5">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted">{entry.from_status ?? '—'}</span>
              <span className="text-muted">→</span>
              <span className="font-medium text-ink">{entry.to_status}</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-muted mt-0.5">
              <Clock size={11} strokeWidth={1.5} />
              <span>{formatDate(entry.created_at)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
