// `cls` estiliza el badge; `bar` es el color sólido para gráficos de barras.
export const STATUS_CONFIG = {
  open:        { label: 'Abierto',      cls: 'bg-accent-subtle text-accent border border-accent/20', bar: 'bg-accent' },
  in_progress: { label: 'En progreso',  cls: 'bg-severity-yellow-bg text-severity-yellow border border-severity-yellow/20', bar: 'bg-severity-yellow' },
  closed:      { label: 'Cerrado',      cls: 'bg-severity-green-bg text-severity-green border border-severity-green/20', bar: 'bg-severity-green' },
  derived:     { label: 'Derivado',     cls: 'bg-gray-100 text-gray-600 border border-gray-200', bar: 'bg-gray-400' },
  pending:     { label: 'Pendiente',    cls: 'bg-gray-100 text-gray-600 border border-gray-200', bar: 'bg-gray-400' },
  active:      { label: 'Activo',       cls: 'bg-severity-green-bg text-severity-green border border-severity-green/20', bar: 'bg-severity-green' },
  inactive:    { label: 'Inactivo',     cls: 'bg-severity-red-bg text-severity-red border border-severity-red/20', bar: 'bg-severity-red' },
}

export default function StatusBadge({ status }) {
  const { label, cls } = STATUS_CONFIG[status] ?? { label: status, cls: 'bg-gray-100 text-gray-600 border border-gray-200' }
  return (
    <span data-testid="status-badge" className={`inline-flex items-center px-2 py-0.5 text-xs font-medium ${cls}`}>
      {label}
    </span>
  )
}
