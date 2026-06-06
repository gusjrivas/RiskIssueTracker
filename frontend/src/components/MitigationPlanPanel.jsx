import { useState, useEffect, useCallback } from 'react'
import { Save, Loader2, AlertTriangle } from 'lucide-react'
import { useBeforeUnload, useNavigate } from 'react-router-dom'
import { useMitigationPlan } from '../hooks/useMitigationPlan'

export default function MitigationPlanPanel({
  entityType, entityId,
  initialMitigation = '', initialContingency = '',
  readOnly = false,
  onDirtyChange,
}) {
  const [mitigation, setMitigation] = useState(initialMitigation)
  const [contingency, setContingency] = useState(initialContingency)
  // Track last-saved values so isDirty resets after a successful save
  const [savedMitigation, setSavedMitigation] = useState(initialMitigation)
  const [savedContingency, setSavedContingency] = useState(initialContingency)
  const [saved, setSaved] = useState(false)
  const [pendingHref, setPendingHref] = useState(null)
  const { saving, error, save } = useMitigationPlan(entityType, entityId)
  const navigate = useNavigate()

  const isDirty = !readOnly && (mitigation !== savedMitigation || contingency !== savedContingency)

  // Notify parent of dirty state so it can guard its own navigate() calls
  useEffect(() => { onDirtyChange?.(isDirty) }, [isDirty, onDirtyChange])

  // Warn on browser tab close / reload
  useBeforeUnload(
    useCallback((e) => { if (isDirty) e.preventDefault() }, [isDirty])
  )

  // Intercept <Link> / <a href="…"> clicks while dirty
  useEffect(() => {
    if (!isDirty) return
    const handleClick = (e) => {
      const anchor = e.target.closest('a[href]')
      if (!anchor) return
      const href = anchor.getAttribute('href')
      if (href && href.startsWith('/')) {
        e.preventDefault()
        e.stopPropagation()
        setPendingHref(href)
      }
    }
    document.addEventListener('click', handleClick, true)
    return () => document.removeEventListener('click', handleClick, true)
  }, [isDirty])

  const executeSave = async () => {
    await save({ mitigation_strategy: mitigation, contingency_plan: contingency })
    setSavedMitigation(mitigation)
    setSavedContingency(contingency)
  }

  const handleSave = async () => {
    try {
      await executeSave()
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch {
      // error shown via hook's error state
    }
  }

  const handleSaveAndLeave = async () => {
    try {
      await executeSave()
      const href = pendingHref
      setPendingHref(null)
      navigate(href)
    } catch {
      // save failed — stay on page, error visible
    }
  }

  const handleDiscardAndLeave = () => {
    const href = pendingHref
    setPendingHref(null)
    navigate(href)
  }

  return (
    <>
      {pendingHref && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-surface border border-border rounded-xl p-6 max-w-sm w-full mx-4 shadow-lg space-y-4">
            <div className="flex items-center gap-3">
              <AlertTriangle size={18} strokeWidth={1.5} className="text-severity-yellow shrink-0" />
              <h3 className="font-display font-semibold">Cambios sin guardar</h3>
            </div>
            <p className="text-sm text-muted leading-relaxed">
              Tenés cambios sin guardar en el plan de mitigación. ¿Querés guardarlos antes de salir?
            </p>
            {error && <p className="text-xs text-severity-red">{error}</p>}
            <div className="flex gap-2 justify-end flex-wrap">
              <button onClick={() => setPendingHref(null)} className="btn-secondary text-sm">
                Cancelar
              </button>
              <button onClick={handleDiscardAndLeave} className="btn-secondary text-sm">
                Salir sin guardar
              </button>
              <button onClick={handleSaveAndLeave} disabled={saving} className="btn-primary text-sm flex items-center gap-2">
                {saving ? <Loader2 size={13} className="animate-spin" /> : <Save size={13} />}
                Guardar y salir
              </button>
            </div>
          </div>
        </div>
      )}

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
    </>
  )
}
