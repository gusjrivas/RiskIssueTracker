import { useState, useEffect, useCallback, useRef } from 'react'
import { Save, Loader2, AlertTriangle } from 'lucide-react'
import { useBeforeUnload, useLocation } from 'react-router-dom'
import { useMitigationPlan } from '../hooks/useMitigationPlan'

export default function MitigationPlanPanel({ entityType, entityId, initialMitigation = '', initialContingency = '', readOnly = false }) {
  const [mitigation, setMitigation] = useState(initialMitigation)
  const [contingency, setContingency] = useState(initialContingency)
  const [saved, setSaved] = useState(false)
  const { saving, error, save } = useMitigationPlan(entityType, entityId)
  const location = useLocation()
  const isDirtyRef = useRef(false)

  const isDirty = !readOnly && (mitigation !== initialMitigation || contingency !== initialContingency)
  isDirtyRef.current = isDirty

  // Advertir al cerrar/recargar la pestaña del navegador
  useBeforeUnload(
    useCallback((e) => {
      if (isDirtyRef.current) e.preventDefault()
    }, [])
  )

  // Interceptar clics en links internos cuando hay cambios sin guardar
  useEffect(() => {
    if (!isDirty) return
    const handleClick = (e) => {
      const anchor = e.target.closest('a[href], button')
      if (!anchor) return
      const href = anchor.getAttribute('href')
      if (href && href.startsWith('/') && !window.confirm('Tenés cambios sin guardar en el plan de mitigación. ¿Salir de todas formas?')) {
        e.preventDefault()
        e.stopPropagation()
      }
    }
    document.addEventListener('click', handleClick, true)
    return () => document.removeEventListener('click', handleClick, true)
  }, [isDirty])

  const handleSave = async () => {
    await save({ mitigation_strategy: mitigation, contingency_plan: contingency })
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="space-y-4">
      {isDirty && !saved && (
        <div className="flex items-center gap-2 text-xs text-severity-yellow">
          <AlertTriangle size={13} strokeWidth={1.5} />
          Cambios sin guardar
        </div>
      )}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Estrategia de mitigación</label>
        <textarea
          value={mitigation}
          onChange={e => !readOnly && setMitigation(e.target.value)}
          rows={3}
          className={`input resize-none ${readOnly ? 'opacity-60 cursor-default' : ''}`}
          placeholder="Describí la estrategia para reducir probabilidad o impacto..."
          readOnly={readOnly}
        />
      </div>
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted uppercase tracking-wide">Plan de contingencia</label>
        <textarea
          value={contingency}
          onChange={e => !readOnly && setContingency(e.target.value)}
          rows={3}
          className={`input resize-none ${readOnly ? 'opacity-60 cursor-default' : ''}`}
          placeholder="¿Qué hacer si el riesgo se materializa?"
          readOnly={readOnly}
        />
      </div>
      {error && <p className="text-xs text-severity-red">{error}</p>}
      {!readOnly && (
        <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-2">
          {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
          {saved ? 'Guardado' : 'Guardar plan'}
        </button>
      )}
    </div>
  )
}
