import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ChevronLeft, Trash2, GitBranch, Lock } from 'lucide-react'
import { getRisk, deleteRisk, transitionRiskStatus, updateRisk } from '../api/risks'
import { deriveIssue } from '../api/issues'
import SeverityBadge from '../components/SeverityBadge'
import StatusBadge from '../components/StatusBadge'
import StatusTransitionButton from '../components/StatusTransitionButton'
import HistoryTimeline from '../components/HistoryTimeline'
import MitigationPlanPanel from '../components/MitigationPlanPanel'
import OwnerField from '../components/OwnerField'
import ActivityLog from '../components/ActivityLog'

const CATEGORY_LABELS = {
  calendario:'Calendario', alcance:'Alcance', ingresos:'Ingresos',
  costos:'Costos', presupuesto:'Presupuesto', equipo:'Equipo', gestion:'Gestión',
}

export default function RiskDetailPage() {
  const { riskId } = useParams()
  const navigate = useNavigate()
  const [risk, setRisk] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deriving, setDeriving] = useState(false)
  const [planDirty, setPlanDirty] = useState(false)

  useEffect(() => {
    getRisk(riskId).then(setRisk).finally(() => setLoading(false))
  }, [riskId])

  const handleTransition = async (status) => {
    const updated = await transitionRiskStatus(riskId, status)
    setRisk(updated)
  }

  const handleDerive = async () => {
    setDeriving(true)
    try {
      const issue = await deriveIssue(riskId)
      const updated = await getRisk(riskId)
      setRisk(updated)
      navigate(`/issues/${issue.id}`)
    } finally {
      setDeriving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('¿Eliminar este riesgo?')) return
    await deleteRisk(riskId)
    navigate(-1)
  }

  const handleOwnerSave = async (newOwnerId) => {
    const updated = await updateRisk(riskId, { owner_id: newOwnerId })
    setRisk(updated)
  }

  if (loading) return (
    <div className="min-h-screen bg-canvas flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-ink border-t-transparent rounded-full animate-spin" />
    </div>
  )

  if (!risk) return null

  const isDerived = risk.status === 'derived'

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border bg-surface">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => {
              if (planDirty && !window.confirm('Tenés cambios sin guardar en el plan. ¿Salir de todas formas?')) return
              navigate(-1)
            }}
            className="text-muted hover:text-ink transition-colors"
          >
            <ChevronLeft size={20} strokeWidth={1.5} />
          </button>
          <span className="text-sm text-muted">Riesgo</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
          <div className="flex items-start justify-between gap-6 mb-8">
            <div>
              <h1 className="font-display text-3xl font-bold leading-tight">{risk.title}</h1>
              <div className="flex items-center gap-3 mt-3">
                <SeverityBadge severity={risk.severity} />
                <StatusBadge status={risk.status} />
                <span className="text-xs text-muted">{CATEGORY_LABELS[risk.category]}</span>
              </div>
            </div>
            <button onClick={handleDelete} className="text-muted hover:text-severity-red transition-colors shrink-0">
              <Trash2 size={18} strokeWidth={1.5} />
            </button>
          </div>

          {risk.description && (
            <p className="text-sm text-muted mb-6 leading-relaxed">{risk.description}</p>
          )}

          <div className="grid grid-cols-3 gap-4 mb-6">
            {[
              ['Probabilidad', risk.probability],
              ['Impacto', risk.impact],
              ['Proximidad', risk.proximity],
            ].map(([label, value]) => (
              <div key={label} className="card">
                <p className="text-xs text-muted uppercase tracking-wide mb-1">{label}</p>
                <p className="font-display font-semibold text-sm capitalize">{value?.replace(/_/g, ' ')}</p>
              </div>
            ))}
          </div>

          <div className="card mb-6">
            <p className="text-xs font-medium text-muted uppercase tracking-wide mb-2">Responsable</p>
            <OwnerField
              ownerId={risk.owner_id}
              onSave={handleOwnerSave}
              readOnly={isDerived}
            />
          </div>

          {isDerived && (
            <div className="flex items-center gap-2 text-sm text-muted bg-surface border border-border rounded-lg px-4 py-3 mb-6">
              <Lock size={14} strokeWidth={1.5} className="shrink-0" />
              Este riesgo se materializó como issue. El seguimiento continúa en el issue — el riesgo es de solo lectura.
              {risk.derived_issue_id && (
                <Link to={`/issues/${risk.derived_issue_id}`} className="ml-auto text-accent hover:underline underline-offset-2 whitespace-nowrap">
                  Ver issue →
                </Link>
              )}
            </div>
          )}

          <div className="flex items-center gap-3 mb-10">
            {!isDerived && (
              <StatusTransitionButton
                currentStatus={risk.status}
                onTransition={handleTransition}
              />
            )}
            {risk.status === 'in_progress' && !risk.derived_issue_id && (
              <button
                onClick={handleDerive}
                disabled={deriving}
                className="btn-secondary flex items-center gap-2"
              >
                <GitBranch size={14} strokeWidth={1.5} />
                {deriving ? 'Derivando...' : 'Derivar a Issue'}
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h2 className="font-display font-semibold mb-4">
                Plan de mitigación
                {isDerived && <span className="ml-2 text-xs text-muted font-normal">(solo lectura)</span>}
              </h2>
              <MitigationPlanPanel
                entityType="risk"
                entityId={riskId}
                initialMitigation={risk.mitigation_strategy ?? ''}
                initialContingency={risk.contingency_plan ?? ''}
                readOnly={isDerived}
                onDirtyChange={setPlanDirty}
              />
            </div>
            <div className="space-y-6">
              <div>
                <h2 className="font-display font-semibold mb-4">Historial de estados</h2>
                <HistoryTimeline entityType="risk" entityId={riskId} />
              </div>
              <div>
                <h2 className="font-display font-semibold mb-4">Actividad</h2>
                <ActivityLog entityType="risk" entityId={riskId} />
              </div>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
