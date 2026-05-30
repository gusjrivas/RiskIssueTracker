import { useState } from 'react'
import { Save, Loader2 } from 'lucide-react'
import { useMitigationPlan } from '../hooks/useMitigationPlan'

export default function MitigationPlanPanel({ entityType, entityId, initialMitigation = '', initialContingency = '' }) {
  const [mitigation, setMitigation] = useState(initialMitigation)
  const [contingency, setContingency] = useState(initialContingency)
  const [saved, setSaved] = useState(false)
  const { saving, error, save } = useMitigationPlan(entityType, entityId)

  const handleSave = async () => {
    await save({ mitigation_strategy: mitigation, contingency_plan: contingency })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Estrategia de mitigación</label>
        <textarea
          value={mitigation}
          onChange={e => setMitigation(e.target.value)}
          rows={3}
          className="input resize-none"
          placeholder="Describí la estrategia para reducir probabilidad o impacto..."
        />
      </div>
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Plan de contingencia</label>
        <textarea
          value={contingency}
          onChange={e => setContingency(e.target.value)}
          rows={3}
          className="input resize-none"
          placeholder="¿Qué hacer si el riesgo se materializa?"
        />
      </div>
      {error && <p className="text-xs text-severity-red">{error}</p>}
      <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2">
        {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
        {saved ? 'Guardado' : 'Guardar plan'}
      </button>
    </div>
  )
}
