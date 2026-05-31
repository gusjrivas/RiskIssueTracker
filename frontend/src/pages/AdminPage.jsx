import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ChevronLeft, CheckCircle, XCircle, Loader2, Users, Pencil, Check, X } from 'lucide-react'
import { useAdmin } from '../hooks/useAdmin'
import StatusBadge from '../components/StatusBadge'

const STATUS_ACTIONS = {
  pending:  { label: 'Aprobar',    action: 'approve',     icon: CheckCircle, cls: 'text-severity-green hover:text-severity-green/80' },
  active:   { label: 'Desactivar', action: 'deactivate',  icon: XCircle,     cls: 'text-severity-red hover:text-severity-red/80'   },
  inactive: { label: 'Reactivar',  action: 'approve',     icon: CheckCircle, cls: 'text-severity-green hover:text-severity-green/80' },
}

export default function AdminPage() {
  const navigate = useNavigate()
  const { data: users, loading, error, approve, deactivate, updateUser } = useAdmin()

  const handleAction = (user) => {
    const cfg = STATUS_ACTIONS[user.status]
    if (!cfg) return
    if (cfg.action === 'approve') approve(user.id)
    else deactivate(user.id)
  }

  const pending = users.filter(u => u.status === 'pending')
  const rest    = users.filter(u => u.status !== 'pending')

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-border bg-white">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <button onClick={() => navigate('/')} className="text-muted hover:text-ink transition-colors">
            <ChevronLeft size={20} strokeWidth={1.5} />
          </button>
          <h1 className="font-display text-xl font-bold">Administración</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>

          {loading && (
            <div className="flex justify-center py-16">
              <Loader2 size={24} className="animate-spin text-muted" />
            </div>
          )}

          {error && <p className="text-sm text-severity-red mb-6">{error}</p>}

          {!loading && (
            <>
              {pending.length > 0 && (
                <section className="mb-10">
                  <h2 className="font-display font-semibold mb-4 flex items-center gap-2">
                    <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-severity-yellow text-white text-xs font-bold">{pending.length}</span>
                    Pendientes de aprobación
                  </h2>
                  <div className="space-y-2">
                    {pending.map(u => (
                      <UserRow key={u.id} user={u} onAction={handleAction} onUpdate={updateUser} />
                    ))}
                  </div>
                </section>
              )}

              <section>
                <h2 className="font-display font-semibold mb-4 flex items-center gap-2">
                  <Users size={16} strokeWidth={1.5} className="text-muted" />
                  Todos los usuarios ({users.length})
                </h2>
                {rest.length === 0 && pending.length === 0 ? (
                  <p className="text-sm text-muted py-8 text-center">No hay usuarios registrados.</p>
                ) : (
                  <div className="space-y-2">
                    {rest.map(u => (
                      <UserRow key={u.id} user={u} onAction={handleAction} onUpdate={updateUser} />
                    ))}
                  </div>
                )}
              </section>
            </>
          )}
        </motion.div>
      </main>
    </div>
  )
}

function UserRow({ user, onAction, onUpdate }) {
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ full_name: user.full_name, email: user.email, role: user.role })
  const [saving, setSaving] = useState(false)
  const [editError, setEditError] = useState(null)

  const cfg = STATUS_ACTIONS[user.status]
  const Icon = cfg?.icon

  const handleSave = async () => {
    setSaving(true)
    setEditError(null)
    try {
      await onUpdate(user.id, form)
      setEditing(false)
    } catch (e) {
      setEditError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setForm({ full_name: user.full_name, email: user.email, role: user.role })
    setEditError(null)
    setEditing(false)
  }

  if (editing) {
    return (
      <div className="card space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-muted uppercase tracking-wide">Nombre</label>
            <input
              value={form.full_name}
              onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
              className="input mt-1"
            />
          </div>
          <div>
            <label className="text-xs text-muted uppercase tracking-wide">Email</label>
            <input
              type="email"
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              className="input mt-1"
            />
          </div>
        </div>
        <div className="w-40">
          <label className="text-xs text-muted uppercase tracking-wide">Rol</label>
          <select
            value={form.role}
            onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
            className="select mt-1"
          >
            <option value="user">user</option>
            <option value="admin">admin</option>
          </select>
        </div>
        {editError && <p className="text-xs text-severity-red">{editError}</p>}
        <div className="flex items-center gap-2">
          <button onClick={handleSave} disabled={saving} className="btn-primary flex items-center gap-1.5 text-sm">
            {saving ? <Loader2 size={13} className="animate-spin" /> : <Check size={13} />}
            Guardar
          </button>
          <button onClick={handleCancel} className="btn-secondary text-sm flex items-center gap-1.5">
            <X size={13} />
            Cancelar
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="card flex items-center justify-between gap-4">
      <div>
        <p className="font-medium text-sm">{user.full_name}</p>
        <p className="text-xs text-muted mt-0.5">{user.email}</p>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        <span className="text-xs text-muted capitalize">{user.role}</span>
        <StatusBadge status={user.status} />
        <button
          onClick={() => setEditing(true)}
          title="Editar usuario"
          className="text-muted hover:text-ink transition-colors"
        >
          <Pencil size={15} strokeWidth={1.5} />
        </button>
        {cfg && (
          <button onClick={() => onAction(user)} title={cfg.label} className={`${cfg.cls} transition-colors`}>
            <Icon size={18} strokeWidth={1.5} />
          </button>
        )}
      </div>
    </div>
  )
}
