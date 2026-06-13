import { SEVERITY_MATRIX, PROXIMITY_LABELS, ZONE_LABELS } from '../utils/severityCalc'
import SeverityCellFlip from './SeverityCellFlip'

const ZONES = ['bajo', 'medio', 'alto']

// Grilla 3×3 de la matriz de severidad (proximidad × zona de exposición).
// Cada celda corresponde a un único valor de severidad 1-9 (la matriz es
// biyectiva). Cada celda es un SeverityCellFlip: muestra conteos y, al
// hacer click, se voltea y lista los riesgos/issues de esa severidad.
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
            return (
              <SeverityCellFlip
                key={zone}
                sev={sev}
                risksCount={risksBySeverity[sev] ?? 0}
                issuesCount={issuesBySeverity[sev] ?? 0}
              />
            )
          })}
        </div>
      ))}
    </div>
  )
}
