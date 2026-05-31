import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, ChevronLeft, Loader2, AlertTriangle, AlertCircle } from 'lucide-react'
import { useRisks } from '../hooks/useRisks'
import { useIssues } from '../hooks/useIssues'
import { getProject } from '../api/projects'
import RiskCard from '../components/RiskCard'
import IssueCard from '../components/IssueCard'
import RiskForm from '../components/RiskForm'
import IssueForm from '../components/IssueForm'

export default function RisksPage() {
  const { projectId } = useParams()
  const { data: risks, loading: loadingRisks, createRisk } = useRisks({ project_id: projectId })
  const { data: issues, loading: loadingIssues, createIssue } = useIssues({ project_id: projectId })
  const [project, setProject] = useState(null)
  const [tab, setTab] = useState('risks')
  const [showForm, setShowForm] = useState(false)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    getProject(projectId).then(setProject).catch(() => {})
  }, [projectId])

  const handleCreateRisk = async (data) => {
    setCreating(true)
    try {
      await createRisk(data)
      setShowForm(false)
    } finally {
      setCreating(false)
    }
  }

  const handleCreateIssue = async (data) => {
    setCreating(true)
    try {
      await createIssue(data)
      setShowForm(false)
    } finally {
      setCreating(false)
    }
  }

  const switchTab = (t) => { setTab(t); setShowForm(false) }

  const projectName = project?.name ?? '…'
  const clientLabel = project?.client ? ` · ${project.client}` : ''

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border bg-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/" className="text-muted hover:text-ink transition-colors">
            <ChevronLeft size={20} strokeWidth={1.5} />
          </Link>
          <div>
            <h1 className="font-display text-xl font-bold leading-tight">{projectName}</h1>
            {project?.client && (
              <p className="text-xs text-muted leading-tight">{project.client}</p>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">

        {/* Tabs */}
        <div className="flex items-center gap-1 border border-border rounded-lg p-1 bg-white w-fit mb-8">
          <button
            onClick={() => switchTab('risks')}
            className={`flex items-center gap-2 px-4 py-2 rounded text-sm font-medium transition-colors ${
              tab === 'risks' ? 'bg-ink text-canvas' : 'text-muted hover:text-ink'
            }`}
          >
            <AlertTriangle size={14} strokeWidth={1.5} />
            Riesgos
            <span className={`text-xs px-1.5 py-0.5 rounded-full ${tab === 'risks' ? 'bg-white/20' : 'bg-border'}`}>
              {risks.length}
            </span>
          </button>
          <button
            onClick={() => switchTab('issues')}
            className={`flex items-center gap-2 px-4 py-2 rounded text-sm font-medium transition-colors ${
              tab === 'issues' ? 'bg-ink text-canvas' : 'text-muted hover:text-ink'
            }`}
          >
            <AlertCircle size={14} strokeWidth={1.5} />
            Issues
            <span className={`text-xs px-1.5 py-0.5 rounded-full ${tab === 'issues' ? 'bg-white/20' : 'bg-border'}`}>
              {issues.length}
            </span>
          </button>
        </div>

        {/* TAB: RIESGOS */}
        {tab === 'risks' && (
          <>
            <div className="flex items-end justify-between mb-8">
              <div>
                <h2 className="font-display text-3xl font-bold">Riesgos</h2>
                <p className="text-muted text-sm mt-1">{risks.length} riesgo{risks.length !== 1 ? 's' : ''}</p>
              </div>
              <button onClick={() => setShowForm(s => !s)} className="btn-primary flex items-center gap-2">
                <Plus size={16} />
                Nuevo riesgo
              </button>
            </div>

            {showForm && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="card mb-8"
              >
                <h3 className="font-display font-semibold mb-5">Nuevo riesgo</h3>
                <RiskForm
                  projectId={projectId}
                  onSubmit={handleCreateRisk}
                  onCancel={() => setShowForm(false)}
                  loading={creating}
                />
              </motion.div>
            )}

            {loadingRisks ? (
              <div className="flex justify-center py-16">
                <Loader2 size={24} className="animate-spin text-muted" />
              </div>
            ) : risks.length === 0 ? (
              <div className="text-center py-16 text-muted">
                <AlertTriangle size={40} className="mx-auto mb-3 opacity-30" strokeWidth={1.5} />
                <p className="text-sm">No hay riesgos registrados. Creá el primero.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {risks.map((r, i) => <RiskCard key={r.id} risk={r} index={i} />)}
              </div>
            )}
          </>
        )}

        {/* TAB: ISSUES */}
        {tab === 'issues' && (
          <>
            <div className="flex items-end justify-between mb-8">
              <div>
                <h2 className="font-display text-3xl font-bold">Issues</h2>
                <p className="text-muted text-sm mt-1">{issues.length} issue{issues.length !== 1 ? 's' : ''}</p>
              </div>
              <button onClick={() => setShowForm(s => !s)} className="btn-primary flex items-center gap-2">
                <Plus size={16} />
                Nuevo issue
              </button>
            </div>

            {showForm && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="card mb-8"
              >
                <h3 className="font-display font-semibold mb-5">Nuevo issue</h3>
                <IssueForm
                  projectId={projectId}
                  onSubmit={handleCreateIssue}
                  onCancel={() => setShowForm(false)}
                  loading={creating}
                />
              </motion.div>
            )}

            {loadingIssues ? (
              <div className="flex justify-center py-16">
                <Loader2 size={24} className="animate-spin text-muted" />
              </div>
            ) : issues.length === 0 ? (
              <div className="text-center py-16 text-muted">
                <AlertCircle size={40} className="mx-auto mb-3 opacity-30" strokeWidth={1.5} />
                <p className="text-sm">No hay issues. Podés crearlo manualmente o derivando un riesgo.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {issues.map((issue, i) => <IssueCard key={issue.id} issue={issue} index={i} />)}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
