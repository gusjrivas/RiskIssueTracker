import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import SeverityMatrixGrid from '../../components/SeverityMatrixGrid'
import * as dashboardApi from '../../api/dashboard'

vi.mock('../../api/dashboard')

const risksBySeverity = { 1: 3, 2: 0, 3: 1, 4: 0, 5: 2, 6: 0, 7: 0, 8: 0, 9: 4 }
const issuesBySeverity = { 1: 1, 2: 0, 3: 0, 4: 5, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0 }

function renderGrid(risks = risksBySeverity, issues = issuesBySeverity) {
  return render(
    <MemoryRouter>
      <SeverityMatrixGrid risksBySeverity={risks} issuesBySeverity={issues} />
    </MemoryRouter>
  )
}

describe('SeverityMatrixGrid', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    dashboardApi.getSeverityItems.mockResolvedValue({ items: [] })
  })

  it('renderiza las 9 celdas de severidad', () => {
    renderGrid()
    for (let s = 1; s <= 9; s++) {
      expect(screen.getByTestId(`matrix-cell-${s}`)).toBeInTheDocument()
    }
  })

  it('colorea cada celda según la zona de severidad', () => {
    renderGrid()
    expect(screen.getByTestId('matrix-cell-2')).toHaveClass('severity-red')
    expect(screen.getByTestId('matrix-cell-5')).toHaveClass('severity-yellow')
    expect(screen.getByTestId('matrix-cell-9')).toHaveClass('severity-green')
  })

  it('muestra el número de severidad como indicador pequeño en la esquina de cada celda', () => {
    renderGrid()
    for (let s = 1; s <= 9; s++) {
      const indicator = screen.getByTestId(`matrix-sev-${s}`)
      expect(indicator).toHaveTextContent(String(s))
      expect(indicator).toHaveClass('absolute', 'bottom-1.5', 'left-2')
    }
  })

  it('muestra los counts de risks e issues dentro de cada celda', () => {
    renderGrid()
    const cell1 = screen.getByTestId('matrix-cell-1')
    expect(cell1).toHaveTextContent('3 riesgos')
    expect(cell1).toHaveTextContent('1 issue')
    const cell4 = screen.getByTestId('matrix-cell-4')
    expect(cell4).toHaveTextContent('0 riesgos')
    expect(cell4).toHaveTextContent('5 issues')
  })

  it('muestra los labels de proximidad y zona en español', () => {
    renderGrid()
    expect(screen.getByText('Corto plazo')).toBeInTheDocument()
    expect(screen.getByText('Mediano plazo')).toBeInTheDocument()
    expect(screen.getByText('Largo plazo')).toBeInTheDocument()
    expect(screen.getByText('Zona Bajo')).toBeInTheDocument()
    expect(screen.getByText('Zona Medio')).toBeInTheDocument()
    expect(screen.getByText('Zona Alto')).toBeInTheDocument()
  })

  it('no rompe si los maps vienen vacíos', () => {
    renderGrid({}, {})
    expect(screen.getByTestId('matrix-cell-1')).toHaveTextContent('0 riesgos')
  })

  it('al hacer click sobre una celda se voltea y pide los riesgos/issues de esa severidad', () => {
    renderGrid()
    fireEvent.click(screen.getByTestId('matrix-cell-1'))
    expect(screen.getByTestId('matrix-cell-back-1')).toBeInTheDocument()
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'risk')
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'issue')
  })
})
