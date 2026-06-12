import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import StatusBarChart from '../../components/StatusBarChart'

const RISK_STATUSES = ['open', 'in_progress', 'closed', 'derived']
const ISSUE_STATUSES = ['open', 'in_progress', 'closed']

describe('StatusBarChart', () => {
  it('renderiza una barra por estado con label en español y count', () => {
    render(
      <StatusBarChart
        title="Riesgos"
        byStatus={{ open: 4, in_progress: 2, closed: 1, derived: 3 }}
        statuses={RISK_STATUSES}
      />
    )
    expect(screen.getByText('Riesgos')).toBeInTheDocument()
    expect(screen.getByTestId('status-bar-open')).toHaveTextContent('Abierto')
    expect(screen.getByTestId('status-bar-open')).toHaveTextContent('4')
    expect(screen.getByTestId('status-bar-in_progress')).toHaveTextContent('En progreso')
    expect(screen.getByTestId('status-bar-closed')).toHaveTextContent('Cerrado')
    expect(screen.getByTestId('status-bar-derived')).toHaveTextContent('Derivado')
  })

  it('no muestra "Derivado" cuando los statuses son de issues', () => {
    render(
      <StatusBarChart
        title="Issues"
        byStatus={{ open: 1, in_progress: 0, closed: 2 }}
        statuses={ISSUE_STATUSES}
      />
    )
    expect(screen.queryByTestId('status-bar-derived')).not.toBeInTheDocument()
    expect(screen.queryByText('Derivado')).not.toBeInTheDocument()
  })

  it('no rompe con todos los counts en 0', () => {
    render(
      <StatusBarChart
        title="Issues"
        byStatus={{ open: 0, in_progress: 0, closed: 0 }}
        statuses={ISSUE_STATUSES}
      />
    )
    expect(screen.getByTestId('status-bar-open')).toHaveTextContent('0')
  })

  it('no rompe si byStatus viene undefined', () => {
    render(<StatusBarChart title="Issues" statuses={ISSUE_STATUSES} />)
    expect(screen.getByTestId('status-bar-open')).toHaveTextContent('0')
  })
})
