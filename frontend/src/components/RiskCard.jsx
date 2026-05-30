import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import SeverityBadge from './SeverityBadge'
import StatusBadge from './StatusBadge'

const CATEGORY_LABELS = {
  calendario: 'Calendario', alcance: 'Alcance', ingresos: 'Ingresos',
  costos: 'Costos', presupuesto: 'Presupuesto', equipo: 'Equipo', gestion: 'Gestión',
}

export default function RiskCard({ risk, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.05, ease: 'easeOut' }}
    >
      <Link to={`/risks/${risk.id}`} className="block card hover:border-ink/30 transition-colors group">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <h3 className="font-display font-semibold text-sm text-ink group-hover:text-accent transition-colors truncate">
              {risk.title}
            </h3>
            <span className="text-xs text-muted mt-0.5 block">
              {CATEGORY_LABELS[risk.category] ?? risk.category}
            </span>
          </div>
          <SeverityBadge severity={risk.severity} />
        </div>
        <div className="mt-4 flex items-center gap-2">
          <StatusBadge status={risk.status} />
          {risk.derived_issue_id && (
            <span className="text-xs text-muted">· Issue derivado</span>
          )}
        </div>
      </Link>
    </motion.div>
  )
}
