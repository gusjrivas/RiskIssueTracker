import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import SeverityMatrixGrid from '../../components/SeverityMatrixGrid'

const risksBySeverity = { 1: 3, 2: 0, 3: 1, 4: 0, 5: 2, 6: 0, 7: 0, 8: 0, 9: 4 }
const issuesBySeverity = { 1: 1, 2: 0, 3: 0, 4: 5, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0 }

describe('SeverityMatrixGrid', () => {
  it('renderiza las 9 celdas de severidad', () => {
    render(<SeverityMatrixGrid risksBySeverity={risksBySeverity} issuesBySeverity={issuesBySeverity} />)
    for (let s = 1; s <= 9; s++) {
      expect(screen.getByTestId(`matrix-cell-${s}`)).toBeInTheDocument()
    }
  })

  it('colorea cada celda según la zona de severidad', () => {
    render(<SeverityMatrixGrid risksBySeverity={risksBySeverity} issuesBySeverity={issuesBySeverity} />)
    expect(screen.getByTestId('matrix-cell-2')).toHaveClass('severity-red')
    expect(screen.getByTestId('matrix-cell-5')).toHaveClass('severity-yellow')
    expect(screen.getByTestId('matrix-cell-9')).toHaveClass('severity-green')
  })

  it('muestra los counts de risks e issues dentro de cada celda', () => {
    render(<SeverityMatrixGrid risksBySeverity={risksBySeverity} issuesBySeverity={issuesBySeverity} />)
    const cell1 = screen.getByTestId('matrix-cell-1')
    expect(cell1).toHaveTextContent('3 riesgos')
    expect(cell1).toHaveTextContent('1 issue')
    const cell4 = screen.getByTestId('matrix-cell-4')
    expect(cell4).toHaveTextContent('0 riesgos')
    expect(cell4).toHaveTextContent('5 issues')
  })

  it('muestra los labels de proximidad y zona en español', () => {
    render(<SeverityMatrixGrid risksBySeverity={risksBySeverity} issuesBySeverity={issuesBySeverity} />)
    expect(screen.getByText('Corto plazo')).toBeInTheDocument()
    expect(screen.getByText('Mediano plazo')).toBeInTheDocument()
    expect(screen.getByText('Largo plazo')).toBeInTheDocument()
    expect(screen.getByText('Zona Bajo')).toBeInTheDocument()
    expect(screen.getByText('Zona Medio')).toBeInTheDocument()
    expect(screen.getByText('Zona Alto')).toBeInTheDocument()
  })

  it('no rompe si los maps vienen vacíos', () => {
    render(<SeverityMatrixGrid risksBySeverity={{}} issuesBySeverity={{}} />)
    expect(screen.getByTestId('matrix-cell-1')).toHaveTextContent('0 riesgos')
  })
})
