import { SEVERITY_MATRIX, PROXIMITY_LABELS, ZONE_LABELS } from '../utils/severityCalc'
import { severityClass } from './SeverityBadge'

const ZONES = ['bajo', 'medio', 'alto']

function plural(n, singular, pluralForm) {
  return `${n} ${n === 1 ? singular : pluralForm}`
}

// Grilla 3×3 de la matriz de severidad (proximidad × zona de exposición).
// Cada celda corresponde a un único valor de severidad 1-9 (la matriz es
// biyectiva), coloreada con la paleta canónica de SeverityBadge.
export default function SeverityMatrixGrid({ risksBySeverity = {}, issuesBySeverity = {} }) {
  return (
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
              <div
                key={zone}
                data-testid={`matrix-cell-${sev}`}
                className={`${severityClass(sev)} flex flex-col items-center justify-center gap-1 py-5 px-3`}
              >
                <span className="font-display text-2xl font-bold leading-none">{sev}</span>
                <span className="text-xs">
                  {plural(risks, 'riesgo', 'riesgos')} · {plural(issues, 'issue', 'issues')}
                </span>
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}
