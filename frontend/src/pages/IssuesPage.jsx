import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ChevronLeft, Trash2, Loader2, AlertCircle } from 'lucide-react'
import { getIssue, deleteIssue, transitionIssueStatus } from '../api/issues'
import SeverityBadge from '../components/SeverityBadge'
import StatusBadge from '../components/StatusBadge'
import StatusTransitionButton from '../components/StatusTransitionButton'
import HistoryTimeline from '../components/HistoryTimeline'
import MitigationPlanPanel from '../components/MitigationPlanPanel'

export default function IssuesPage() {
  const { issueId } = useParams()
  const navigate = useNavigate()
  const [issue, setIssue] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getIssue(issueId).then(setIssue).finally(() => setLoading(false))
  }, [issueId])

  const handleTransition = async (status) => {
    const updated = await transitionIssueStatus(issueId, status)
    setIssue(updated)
  }

  const handleDelete = async () => {
    if (!confirm('¿Eliminar este issue?')) return
    await deleteIssue(issueId)
    navigate(-1)
  }

  if (loading) return (
    <div className="min-h-screen bg-canvas flex items-center justify-center">
      <Loader2 size={24} className="animate-spin text-muted" />
    </div>
  )

  if (!issue) return null

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border bg-white">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="text-muted hover:text-ink transition-colors">
            <ChevronLeft size={20} strokeWidth={1.5} />
          </button>
          <span className="text-sm text-muted">Issue</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
          <div className="flex items-start justify-between gap-6 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle size={16} strokeWidth={1.5} className="text-muted" />
                <span className="text-xs text-muted uppercase tracking-wide">Issue</span>
              </div>
              <h1 className="font-display text-3xl font-bold leading-tight">{issue.title}</h1>
              <div className="flex items-center gap-3 mt-3">
                <SeverityBadge severity={issue.severity} />
                <StatusBadge status={issue.status} />
              </div>
            </div>
            <button onClick={handleDelete} className="text-muted hover:text-severity-red transition-colors shrink-0">
              <Trash2 size={18} strokeWidth={1.5} />
            </button>
          </div>

          {issue.description && (
            <p className="text-sm text-muted mb-8 leading-relaxed">{issue.description}</p>
          )}

          {issue.risk_id && (
            <div className="mb-6 text-sm">
              <Link to={`/risks/${issue.risk_id}`} className="text-accent hover:underline underline-offset-2">
                ← Ver riesgo origen
              </Link>
            </div>
          )}

          <div className="mb-10">
            <StatusTransitionButton currentStatus={issue.status} onTransition={handleTransition} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div>
              <h2 className="font-display font-semibold mb-4">Plan de mitigación</h2>
              <MitigationPlanPanel
                entityType="issue"
                entityId={issueId}
                initialMitigation={issue.mitigation_strategy ?? ''}
                initialContingency={issue.contingency_plan ?? ''}
              />
            </div>
            <div>
              <h2 className="font-display font-semibold mb-4">Historial</h2>
              <HistoryTimeline entityType="issue" entityId={issueId} />
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
