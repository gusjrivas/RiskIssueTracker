import { useState } from 'react'
import { Loader2 } from 'lucide-react'

const CATEGORIES = ['calendario','alcance','ingresos','costos','presupuesto','equipo','gestion']
const PROBABILITY = ['muy_baja','baja','media','alta','muy_alta']
const IMPACT = ['muy_bajo','bajo','medio','alto','muy_alto']
const PROXIMITY = ['corto_plazo','mediano_plazo','largo_plazo']

const LABELS = {
  muy_baja:'Muy baja', baja:'Baja', media:'Media', alta:'Alta', muy_alta:'Muy alta',
  muy_bajo:'Muy bajo', bajo:'Bajo', medio:'Medio', alto:'Alto', muy_alto:'Muy alto',
  corto_plazo:'Corto plazo', mediano_plazo:'Mediano plazo', largo_plazo:'Largo plazo',
  calendario:'Calendario', alcance:'Alcance', ingresos:'Ingresos',
  costos:'Costos', presupuesto:'Presupuesto', equipo:'Equipo', gestion:'Gestión',
}

const EMPTY = { title: '', description: '', category: '', probability: '', impact: '', proximity: '', mitigation_strategy: '', contingency_plan: '' }

export default function RiskForm({ projectId, initial = {}, onSubmit, onCancel, loading = false }) {
  const [form, setForm] = useState({ ...EMPTY, ...initial })
  const [error, setError] = useState(null)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    try {
      await onSubmit({ ...form, project_id: projectId })
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Título *</label>
        <input value={form.title} onChange={set('title')} required className="input" placeholder="Ej: Retraso en entrega de componentes" />
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Descripción</label>
        <textarea value={form.description} onChange={set('description')} rows={2} className="input resize-none" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted uppercase tracking-wide">Categoría *</label>
          <select value={form.category} onChange={set('category')} required className="select">
            <option value="">Seleccioná</option>
            {CATEGORIES.map(c => <option key={c} value={c}>{LABELS[c]}</option>)}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted uppercase tracking-wide">Proximidad *</label>
          <select value={form.proximity} onChange={set('proximity')} required className="select">
            <option value="">Seleccioná</option>
            {PROXIMITY.map(p => <option key={p} value={p}>{LABELS[p]}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted uppercase tracking-wide">Probabilidad *</label>
          <select value={form.probability} onChange={set('probability')} required className="select">
            <option value="">Seleccioná</option>
            {PROBABILITY.map(p => <option key={p} value={p}>{LABELS[p]}</option>)}
          </select>
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-muted uppercase tracking-wide">Impacto *</label>
          <select value={form.impact} onChange={set('impact')} required className="select">
            <option value="">Seleccioná</option>
            {IMPACT.map(i => <option key={i} value={i}>{LABELS[i]}</option>)}
          </select>
        </div>
      </div>

      {error && <p className="text-xs text-severity-red">{error}</p>}

      <div className="flex items-center gap-3 pt-2">
        <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
          {loading && <Loader2 size={14} className="animate-spin" />}
          {initial.id ? 'Guardar cambios' : 'Crear riesgo'}
        </button>
        {onCancel && <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>}
      </div>
    </form>
  )
}
