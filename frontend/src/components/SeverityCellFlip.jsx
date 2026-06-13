import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { X } from 'lucide-react'
import { severityClass } from './SeverityBadge'
import StatusBadge from './StatusBadge'
import { useSeverityItems } from '../hooks/useSeverityItems'

function plural(n, singular, pluralForm) {
  return `${n} ${n === 1 ? singular : pluralForm}`
}

function ItemList({ items, loading, error, emptyLabel, basePath }) {
  if (loading) {
    return <p className="text-[10px] text-muted">Cargando...</p>
  }
  if (error) {
    return <p className="text-[10px] text-red-500">Error al cargar.</p>
  }
  if (!items || items.length === 0) {
    return <p className="text-[10px] text-muted">{emptyLabel}</p>
  }
  return (
    <div className="space-y-1">
      {items.map(item => (
        <Link
          key={item.id}
          to={`${basePath}/${item.id}`}
          className="flex items-center justify-between gap-2 text-[11px] hover:underline"
        >
          <span className="truncate">{item.title}</span>
          <StatusBadge status={item.status} />
        </Link>
      ))}
    </div>
  )
}

// Celda de la matriz de severidad con flip 3D: la cara frontal muestra los
// conteos (igual que antes); al hacer click se voltea y la cara trasera
// lista los riesgos/issues de esa severidad, con link directo al detalle.
export default function SeverityCellFlip({ sev, risksCount, issuesCount }) {
  const [flipped, setFlipped] = useState(false)
  const { itemsByKey, loadingByKey, errorByKey, fetchItems } = useSeverityItems()

  const openBack = () => {
    fetchItems(sev, 'risk')
    fetchItems(sev, 'issue')
    setFlipped(true)
  }

  return (
    <div className="relative" style={{ perspective: '1000px' }}>
      <motion.div
        className="relative w-full"
        style={{ transformStyle: 'preserve-3d' }}
        animate={{ rotateY: flipped ? 180 : 0 }}
        transition={{ duration: 0.4, ease: 'easeInOut' }}
      >
        <button
          type="button"
          onClick={openBack}
          data-testid={`matrix-cell-${sev}`}
          tabIndex={flipped ? -1 : 0}
          aria-hidden={flipped}
          style={{ backfaceVisibility: 'hidden' }}
          className={`${severityClass(sev)} relative flex flex-col items-center justify-center gap-1.5 py-6 px-3 w-full`}
        >
          <span className="font-display text-2xl font-bold leading-none">
            {plural(risksCount, 'riesgo', 'riesgos')}
          </span>
          <span className="font-display text-lg font-semibold leading-none opacity-75">
            {plural(issuesCount, 'issue', 'issues')}
          </span>
          <span
            data-testid={`matrix-sev-${sev}`}
            className="absolute bottom-1.5 left-2 text-[10px] font-medium opacity-50 leading-none"
          >
            {sev}
          </span>
        </button>

        {flipped && (
          <div
            data-testid={`matrix-cell-back-${sev}`}
            style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
            className="absolute inset-0 flex flex-col gap-2 p-2 bg-surface border border-border overflow-hidden"
          >
            <button
              type="button"
              data-testid={`flip-close-${sev}`}
              onClick={() => setFlipped(false)}
              className="self-end text-muted hover:text-ink"
            >
              <X size={12} />
            </button>

            <div className="flex-1 overflow-y-auto max-h-24">
              <p className="text-[10px] font-semibold text-muted mb-1">Riesgos</p>
              <ItemList
                items={itemsByKey[`${sev}-risk`]}
                loading={loadingByKey[`${sev}-risk`]}
                error={errorByKey[`${sev}-risk`]}
                emptyLabel="No hay riesgos con esta severidad."
                basePath="/risks"
              />
            </div>

            <div className="flex-1 overflow-y-auto max-h-24">
              <p className="text-[10px] font-semibold text-muted mb-1">Issues</p>
              <ItemList
                items={itemsByKey[`${sev}-issue`]}
                loading={loadingByKey[`${sev}-issue`]}
                error={errorByKey[`${sev}-issue`]}
                emptyLabel="No hay issues con esta severidad."
                basePath="/issues"
              />
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
