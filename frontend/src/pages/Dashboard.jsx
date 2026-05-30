import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, FolderOpen, Loader2 } from 'lucide-react'
import { useProjects } from '../hooks/useProjects'
import { useAuth } from '../hooks/useAuth'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const { data: projects, loading, createProject } = useProjects()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [creating, setCreating] = useState(false)

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!name.trim()) return
    setCreating(true)
    try {
      await createProject({ name })
      setName('')
      setShowForm(false)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border bg-white">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="font-display text-xl font-bold">RiskTracker</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted">{user?.full_name}</span>
            <button onClick={logout} className="text-sm text-muted hover:text-ink transition-colors">
              Salir
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="font-display text-3xl font-bold">Proyectos</h2>
            <p className="text-muted text-sm mt-1">{projects.length} proyecto{projects.length !== 1 ? 's' : ''}</p>
          </div>
          <button onClick={() => setShowForm(s => !s)} className="btn-primary flex items-center gap-2">
            <Plus size={16} />
            Nuevo proyecto
          </button>
        </div>

        {showForm && (
          <motion.form
            onSubmit={handleCreate}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="card mb-6 flex gap-3"
          >
            <input
              autoFocus
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Nombre del proyecto"
              className="input"
              required
            />
            <button type="submit" disabled={creating} className="btn-primary flex items-center gap-2 whitespace-nowrap">
              {creating && <Loader2 size={14} className="animate-spin" />}
              Crear
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="btn-secondary whitespace-nowrap">
              Cancelar
            </button>
          </motion.form>
        )}

        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 size={24} className="animate-spin text-muted" />
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-16 text-muted">
            <FolderOpen size={40} className="mx-auto mb-3 opacity-30" strokeWidth={1.5} />
            <p className="text-sm">No hay proyectos todavía. Creá el primero.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p, i) => (
              <motion.div
                key={p.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.22, delay: i * 0.05, ease: 'easeOut' }}
              >
                <Link to={`/projects/${p.id}/risks`} className="block card hover:border-ink/30 transition-colors group h-full">
                  <FolderOpen size={20} strokeWidth={1.5} className="text-muted mb-3 group-hover:text-accent transition-colors" />
                  <h3 className="font-display font-semibold text-sm group-hover:text-accent transition-colors">{p.name}</h3>
                  {p.client && <p className="text-xs text-muted mt-1">{p.client}</p>}
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
