import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import SeverityCellFlip from '../../components/SeverityCellFlip'
import * as useSeverityItemsModule from '../../hooks/useSeverityItems'

vi.mock('../../hooks/useSeverityItems')

function setup({ itemsByKey = {}, loadingByKey = {}, errorByKey = {} } = {}, props = {}) {
  const fetchItems = vi.fn()
  useSeverityItemsModule.useSeverityItems.mockReturnValue({
    itemsByKey,
    loadingByKey,
    errorByKey,
    fetchItems,
  })
  render(
    <MemoryRouter>
      <SeverityCellFlip sev={1} risksCount={2} issuesCount={1} {...props} />
    </MemoryRouter>
  )
  return { fetchItems }
}

describe('SeverityCellFlip', () => {
  it('muestra la cara frontal con los conteos y el número de severidad', () => {
    setup()
    const front = screen.getByTestId('matrix-cell-1')
    expect(front).toHaveTextContent('2 riesgos')
    expect(front).toHaveTextContent('1 issue')
    expect(screen.getByTestId('matrix-sev-1')).toHaveTextContent('1')
    expect(screen.queryByTestId('matrix-cell-back-1')).not.toBeInTheDocument()
  })

  it('al hacer click se voltea, muestra la cara trasera y dispara fetchItems para risk e issue', () => {
    const { fetchItems } = setup({ itemsByKey: { '1-risk': [], '1-issue': [] } })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    expect(screen.getByTestId('matrix-cell-back-1')).toBeInTheDocument()
    expect(fetchItems).toHaveBeenCalledWith(1, 'risk')
    expect(fetchItems).toHaveBeenCalledWith(1, 'issue')
  })

  it('renderiza links a riesgos e issues con su StatusBadge', () => {
    setup({
      itemsByKey: {
        '1-risk': [{ id: 'r1', title: 'Riesgo crítico', status: 'open' }],
        '1-issue': [{ id: 'i1', title: 'Issue crítico', status: 'closed' }],
      },
    })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    const riskLink = screen.getByRole('link', { name: /Riesgo crítico/ })
    expect(riskLink).toHaveAttribute('href', '/risks/r1')

    const issueLink = screen.getByRole('link', { name: /Issue crítico/ })
    expect(issueLink).toHaveAttribute('href', '/issues/i1')
  })

  it('muestra mensajes cuando no hay riesgos ni issues para la severidad', () => {
    setup({ itemsByKey: { '1-risk': [], '1-issue': [] } })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    expect(screen.getByText('No hay riesgos con esta severidad.')).toBeInTheDocument()
    expect(screen.getByText('No hay issues con esta severidad.')).toBeInTheDocument()
  })

  it('el botón de cierre vuelve a la cara frontal', () => {
    setup({ itemsByKey: { '1-risk': [], '1-issue': [] } })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))
    expect(screen.getByTestId('matrix-cell-back-1')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('flip-close-1'))
    expect(screen.queryByTestId('matrix-cell-back-1')).not.toBeInTheDocument()
  })

  it('muestra un mensaje de error si fetchItems falló para riesgos, sin afectar la sección de issues', () => {
    setup({
      itemsByKey: { '1-issue': [] },
      errorByKey: { '1-risk': 'boom' },
    })

    fireEvent.click(screen.getByTestId('matrix-cell-1'))

    expect(screen.getByText('Error al cargar.')).toBeInTheDocument()
    expect(screen.queryByText('No hay riesgos con esta severidad.')).not.toBeInTheDocument()
    expect(screen.getByText('No hay issues con esta severidad.')).toBeInTheDocument()
  })

  it('el botón frontal deja de ser focuseable y se oculta de lectores de pantalla al voltear', () => {
    setup({ itemsByKey: { '1-risk': [], '1-issue': [] } })

    const front = screen.getByTestId('matrix-cell-1')
    expect(front).toHaveAttribute('tabIndex', '0')
    expect(front).toHaveAttribute('aria-hidden', 'false')

    fireEvent.click(front)

    expect(front).toHaveAttribute('tabIndex', '-1')
    expect(front).toHaveAttribute('aria-hidden', 'true')
  })
})
