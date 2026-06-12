import { motion } from 'framer-motion'
import { STATUS_CONFIG } from './StatusBadge'

// Barras horizontales de cantidades por estado. `statuses` define qué estados
// mostrar y en qué orden (risks incluye 'derived', issues no).
export default function StatusBarChart({ title, byStatus = {}, statuses }) {
  const max = Math.max(...statuses.map(s => byStatus[s] ?? 0), 1)

  return (
    <div>
      <h3 className="font-display font-semibold text-sm mb-4">{title}</h3>
      <div className="space-y-3">
        {statuses.map(status => {
          const count = byStatus[status] ?? 0
          const pct = (count / max) * 100
          return (
            <div key={status} data-testid={`status-bar-${status}`} className="flex items-center gap-3">
              <span className="text-xs text-muted w-24 shrink-0">
                {STATUS_CONFIG[status]?.label ?? status}
              </span>
              <div className="flex-1 h-5 bg-border/40">
                <motion.div
                  data-testid={`status-bar-fill-${status}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                  className={`h-full ${STATUS_CONFIG[status]?.bar ?? 'bg-gray-400'}`}
                />
              </div>
              <span className="font-display text-sm font-bold w-8 text-right">{count}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
