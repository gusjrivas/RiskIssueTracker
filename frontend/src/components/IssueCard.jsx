import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import SeverityBadge from './SeverityBadge'
import StatusBadge from './StatusBadge'

export default function IssueCard({ issue, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.05, ease: 'easeOut' }}
    >
      <Link to={`/issues/${issue.id}`} className="block card hover:border-ink/30 transition-colors group">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 mb-1">
              <AlertCircle size={12} strokeWidth={1.5} className="text-muted shrink-0" />
              <span className="text-xs text-muted">Issue</span>
            </div>
            <h3 className="font-display font-semibold text-sm text-ink group-hover:text-accent transition-colors truncate">
              {issue.title}
            </h3>
          </div>
          <SeverityBadge severity={issue.severity} />
        </div>
        <div className="mt-4 flex items-center gap-2">
          <StatusBadge status={issue.status} />
          {issue.risk_id && (
            <span className="text-xs text-muted">· Derivado de riesgo</span>
          )}
        </div>
      </Link>
    </motion.div>
  )
}
