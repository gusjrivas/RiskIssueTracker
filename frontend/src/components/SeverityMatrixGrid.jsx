import { useState } from 'react'
import { SEVERITY_MATRIX, PROXIMITY_LABELS, ZONE_LABELS } from '../utils/severityCalc'
import { severityClass } from './SeverityBadge'
import SeverityDrawer from './SeverityDrawer'

const ZONES = ['bajo', 'medio', 'alto']

function plural(n, singular, pluralForm) {
  return `${n} ${n === 1 ? singular : pluralForm}`
}

// Grilla 3×3 de la matriz de severidad (proximidad × zona de exposición).
// Cada celda corresponde a un único valor de severidad 1-9 (la matriz es
// biyectiva). Cualquier celda hace toggle de la bandeja única (SeverityDrawer)
// debajo de la grilla, que lista todos los riesgos/issues agrupados por
// severidad.
export default function SeverityMatrixGrid({
  risksBySeverity = {},
  issuesBySeverity = {},
  groups,
  groupsLoading,
  groupsError,
  onOpenDrawer,
}) {
  const [open, setOpen] = useState(false)

  const toggleDrawer = () => {
    if (!open) onOpenDrawer()
    setOpen(o => !o)
  }

  return (
    <div>
      <div className="grid grid-cols-[auto_1fr_1fr_1fr] gap-2">
        <div />
        {ZONES.map(zone => (
          <div key={zone} className="text-xs font-medium text-muted text-center pb-1">
            Zona {ZONE_LABELS[zone]}
          </div>
        ))}

        {Object.entries(SEVERITY_MATRIX).map(([proximity, row]) => (
          <div key={proximity} className="contents">
            <div className="text-xs font-medium text-muted flex items-center pr-2">
              {PROXIMITY_LABELS[proximity]}
            </div>
            {ZONES.map(zone => {
              const sev = row[zone]
              const risks = risksBySeverity[sev] ?? 0
              const issues = issuesBySeverity[sev] ?? 0
              return (
                <button
                  key={zone}
                  type="button"
                  onClick={toggleDrawer}
                  data-testid={`matrix-cell-${sev}`}
                  className={`${severityClass(sev)} relative flex flex-col items-center justify-center gap-1.5 py-6 px-3 w-full`}
                >
                  <span className="font-display text-2xl font-bold leading-none">
                    {plural(risks, 'riesgo', 'riesgos')}
                  </span>
                  <span className="font-display text-lg font-semibold leading-none opacity-75">
                    {plural(issues, 'issue', 'issues')}
                  </span>
                  <span
                    data-testid={`matrix-sev-${sev}`}
                    className="absolute bottom-1.5 left-2 text-[10px] font-medium opacity-50 leading-none"
                  >
                    {sev}
                  </span>
                </button>
              )
            })}
          </div>
        ))}
      </div>

      <SeverityDrawer groups={groups} loading={groupsLoading} error={groupsError} open={open} />
    </div>
  )
}
