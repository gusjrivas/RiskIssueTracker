import { Loader2, PenLine, UserCheck, GitCommit, Trash2, Plus, ArrowRight } from 'lucide-react'
import { useActivity } from '../hooks/useActivity'

const FIELD_LABELS = {
  title: 'Título',
  description: 'Descripción',
  category: 'Categoría',
  probability: 'Probabilidad',
  impact: 'Impacto',
  proximity: 'Proximidad',
  severity: 'Severidad',
  mitigation_strategy: 'Estrategia de mitigación',
  contingency_plan: 'Plan de contingencia',
}

const ACTION_ICONS = {
  create: <Plus size={13} strokeWidth={1.5} className="text-accent shrink-0 mt-0.5" />,
  update: <PenLine size={13} strokeWidth={1.5} className="text-muted shrink-0 mt-0.5" />,
  owner_change: <UserCheck size={13} strokeWidth={1.5} className="text-severity-yellow shrink-0 mt-0.5" />,
  status_change: <GitCommit size={13} strokeWidth={1.5} className="text-accent shrink-0 mt-0.5" />,
  delete: <Trash2 size={13} strokeWidth={1.5} className="text-severity-red shrink-0 mt-0.5" />,
  derive: <ArrowRight size={13} strokeWidth={1.5} className="text-muted shrink-0 mt-0.5" />,
}

const STATUS_LABELS = {
  open: 'Abierto', in_progress: 'En progreso', closed: 'Cerrado', derived: 'Derivado',
}

function formatDate(iso) {
  return new Date(iso).toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function ChangeDetail({ action, changes }) {
  if (!changes) return null

  if (action === 'owner_change') {
    const from = changes.from_name ?? 'Sin responsable'
    const to = changes.to_name ?? 'Sin responsable'
    return (
      <p className="text-xs text-muted mt-0.5">
        {from} → {to}
      </p>
    )
  }

  if (action === 'status_change') {
    return (
      <p className="text-xs text-muted mt-0.5">
        {STATUS_LABELS[changes.from] ?? changes.from} → {STATUS_LABELS[changes.to] ?? changes.to}
      </p>
    )
  }

  if (action === 'update') {
    const lines = Object.entries(changes)
      .filter(([key]) => key !== 'severity' || changes.severity)
      .map(([key, val]) => {
        if (key === 'owner') {
          return `Responsable: ${val.from_name ?? 'ninguno'} → ${val.to_name ?? 'ninguno'}`
        }
        const label = FIELD_LABELS[key] ?? key
        const from = val?.from ?? '—'
        const to = val?.to ?? '—'
        const truncate = (s) => s && s.length > 40 ? s.slice(0, 40) + '…' : s
        return `${label}: ${truncate(from)} → ${truncate(to)}`
      })

    if (lines.length === 0) return null
    return (
      <ul className="mt-0.5 space-y-0.5">
        {lines.map((line, i) => (
          <li key={i} className="text-xs text-muted">{line}</li>
        ))}
      </ul>
    )
  }

  if (action === 'create' && changes?.owner_name) {
    return <p className="text-xs text-muted mt-0.5">Responsable: {changes.owner_name}</p>
  }

  return null
}

function actionLabel(action) {
  switch (action) {
    case 'create': return 'Creó'
    case 'update': return 'Modificó'
    case 'owner_change': return 'Cambió responsable'
    case 'status_change': return 'Cambió estado'
    case 'delete': return 'Eliminó'
    case 'derive': return 'Derivó a issue'
    default: return action
  }
}

export default function ActivityLog({ entityType, entityId }) {
  const { entries, loading, error } = useActivity(entityType, entityId)

  if (loading) return (
    <div className="flex items-center gap-2 text-xs text-muted py-4">
      <Loader2 size={13} className="animate-spin" /> Cargando actividad…
    </div>
  )

  if (error) return <p className="text-xs text-severity-red">{error}</p>

  if (entries.length === 0) return (
    <p className="text-xs text-muted">Sin actividad registrada.</p>
  )

  return (
    <ol className="space-y-3">
      {entries.map(entry => (
        <li key={entry.id} className="flex gap-2.5">
          {ACTION_ICONS[entry.action] ?? ACTION_ICONS.update}
          <div className="min-w-0">
            <p className="text-xs leading-snug">
              <span className="font-medium">{entry.editor_name ?? 'Sistema'}</span>
              {' '}{actionLabel(entry.action)}
            </p>
            <ChangeDetail action={entry.action} changes={entry.changes} />
            <p className="text-[11px] text-muted mt-0.5">{formatDate(entry.created_at)}</p>
          </div>
        </li>
      ))}
    </ol>
  )
}
