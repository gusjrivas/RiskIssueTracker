import { Link } from 'react-router-dom'
import SeverityBadge from './SeverityBadge'
import StatusBadge from './StatusBadge'

const TYPE_LABELS = { risk: 'Riesgo', issue: 'Issue' }
const BASE_PATHS = { risk: '/risks', issue: '/issues' }

// Bandeja única debajo de la matriz de severidad: lista todos los
// riesgos/issues visibles para el usuario, agrupados por severidad
// (1 = más crítico, primero). Puramente presentacional: recibe todo por
// props, sin fetch propio.
export default function SeverityDrawer({ groups, loading, error, open }) {
  if (!open) return null

  return (
    <div id="severity-drawer" data-testid="severity-drawer" className="card mt-2 space-y-4">
      {loading ? (
        <p className="text-sm text-muted">Cargando...</p>
      ) : error ? (
        <p className="text-sm text-red-500">Error al cargar.</p>
      ) : !groups || groups.length === 0 ? (
        <p className="text-sm text-muted">No hay riesgos ni issues para mostrar.</p>
      ) : (
        groups.map(group => (
          <div key={group.severity} data-testid={`severity-group-${group.severity}`}>
            <SeverityBadge severity={group.severity} />
            <div className="mt-2 space-y-1.5">
              {group.items.map(item => (
                <Link
                  key={`${item.type}-${item.id}`}
                  to={`${BASE_PATHS[item.type]}/${item.id}`}
                  className="flex flex-wrap items-center justify-between gap-2 text-sm hover:underline"
                >
                  <span className="flex items-center gap-2 min-w-0">
                    <span className="text-[10px] uppercase text-muted shrink-0">
                      {TYPE_LABELS[item.type]}
                    </span>
                    <span className="truncate">{item.title}</span>
                  </span>
                  <StatusBadge status={item.status} />
                </Link>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
