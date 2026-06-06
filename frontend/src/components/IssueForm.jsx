import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { useUsers } from '../hooks/useUsers'

const SEVERITY_OPTIONS = [
  { value: 1, label: '1 — Crítico' },
  { value: 2, label: '2 — Crítico' },
  { value: 3, label: '3 — Crítico' },
  { value: 4, label: '4 — Moderado' },
  { value: 5, label: '5 — Moderado' },
  { value: 6, label: '6 — Moderado' },
  { value: 7, label: '7 — Bajo' },
  { value: 8, label: '8 — Bajo' },
  { value: 9, label: '9 — Bajo' },
]

const EMPTY = { title: '', description: '', severity: '', owner_id: '' }

export default function IssueForm({ projectId, onSubmit, onCancel, loading = false }) {
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState(null)
  const { users, loading: loadingUsers } = useUsers()

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    try {
      await onSubmit({
        ...form,
        project_id: projectId,
        severity: Number(form.severity),
        owner_id: form.owner_id === '' ? null : form.owner_id,
      })
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Título *</label>
        <input
          value={form.title}
          onChange={set('title')}
          required
          className="input"
          placeholder="Ej: Falla en módulo de pagos"
        />
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Descripción</label>
        <textarea
          value={form.description}
          onChange={set('description')}
          rows={2}
          className="input resize-none"
          placeholder="Descripción del problema..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted uppercase tracking-wide">Severidad *</label>
          <select value={form.severity} onChange={set('severity')} required className="select">
            <option value="">Seleccioná</option>
            {SEVERITY_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted uppercase tracking-wide">Responsable</label>
          <select value={form.owner_id} onChange={set('owner_id')} className="select" disabled={loadingUsers}>
            <option value="">Sin responsable</option>
            {users.map(u => <option key={u.id} value={u.id}>{u.full_name}</option>)}
          </select>
        </div>
      </div>

      {error && <p className="text-xs text-severity-red">{error}</p>}

      <div className="flex items-center gap-3 pt-1">
        <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
          {loading && <Loader2 size={14} className="animate-spin" />}
          Crear issue
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>
        )}
      </div>
    </form>
  )
}
