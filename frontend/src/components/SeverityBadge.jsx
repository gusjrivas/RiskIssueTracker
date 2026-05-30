const LABELS = { 1:'Crítico',2:'Crítico',3:'Crítico',4:'Moderado',5:'Moderado',6:'Moderado',7:'Bajo',8:'Bajo',9:'Bajo' }

function severityClass(s) {
  if (s <= 3) return 'severity-red'
  if (s <= 6) return 'severity-yellow'
  return 'severity-green'
}

export default function SeverityBadge({ severity }) {
  return (
    <span
      data-testid="severity-badge"
      className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium ${severityClass(severity)}`}
    >
      <span className="font-display font-bold">{severity}</span>
      <span>{LABELS[severity]}</span>
    </span>
  )
}
