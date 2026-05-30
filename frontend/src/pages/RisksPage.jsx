import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, ChevronLeft, Loader2, AlertTriangle } from 'lucide-react'
import { useRisks } from '../hooks/useRisks'
import RiskCard from '../components/RiskCard'
import RiskForm from '../components/RiskForm'

export default function RisksPage() {
  const { projectId } = useParams()
  const { data: risks, loading, createRisk } = useRisks({ project_id: projectId })
  const [showForm, setShowForm] = useState(false)
  const [creating, setCreating] = useState(false)

  const handleCreate = async (data) => {
    setCreating(true)
    try {
      await createRisk(data)
      setShowForm(false)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border bg-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-4">
          <Link to="/" className="text-muted hover:text-ink transition-colors">
            <ChevronLeft size={20} strokeWidth={1.5} />
          </Link>
          <h1 className="font-display text-xl font-bold">Riesgos</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="font-display text-3xl font-bold">Riesgos del proyecto</h2>
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
              onSubmit={handleCreate}
              onCancel={() => setShowForm(false)}
              loading={creating}
            />
          </motion.div>
        )}

        {loading ? (
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
      </main>
    </div>
  )
}
