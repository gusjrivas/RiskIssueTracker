import { useState } from 'react'
import { User, Pencil, Check, X, Loader2 } from 'lucide-react'
import { useUsers } from '../hooks/useUsers'

export default function OwnerField({ ownerId, onSave, readOnly = false }) {
  const { users, loading: loadingUsers } = useUsers()
  const [editing, setEditing] = useState(false)
  const [selected, setSelected] = useState(ownerId ?? '')
  const [saving, setSaving] = useState(false)

  const currentOwner = users.find(u => u.id === ownerId)

  const handleSave = async () => {
    setSaving(true)
    try {
      await onSave(selected === '' ? null : selected)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setSelected(ownerId ?? '')
    setEditing(false)
  }

  if (!editing) {
    return (
      <div className="flex items-center gap-2 min-h-[28px]">
        <User size={13} strokeWidth={1.5} className="text-muted shrink-0" />
        <span className="text-sm">
          {currentOwner ? currentOwner.full_name : <span className="text-muted italic">Sin responsable</span>}
        </span>
        {!readOnly && (
          <button
            onClick={() => { setSelected(ownerId ?? ''); setEditing(true) }}
            className="text-muted hover:text-ink transition-colors ml-1"
            title="Cambiar responsable"
          >
            <Pencil size={12} strokeWidth={1.5} />
          </button>
        )}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <User size={13} strokeWidth={1.5} className="text-muted shrink-0" />
      <select
        value={selected}
        onChange={e => setSelected(e.target.value)}
        className="select text-sm py-1 h-auto"
        disabled={loadingUsers || saving}
        autoFocus
      >
        <option value="">Sin responsable</option>
        {users.map(u => (
          <option key={u.id} value={u.id}>{u.full_name}</option>
        ))}
      </select>
      <button
        onClick={handleSave}
        disabled={saving}
        className="text-accent hover:text-ink transition-colors"
        title="Guardar"
      >
        {saving ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} strokeWidth={1.5} />}
      </button>
      <button
        onClick={handleCancel}
        className="text-muted hover:text-ink transition-colors"
        title="Cancelar"
      >
        <X size={14} strokeWidth={1.5} />
      </button>
    </div>
  )
}
