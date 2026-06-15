import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import SeverityDrawer from '../../components/SeverityDrawer'

function renderDrawer(props = {}) {
  return render(
    <MemoryRouter>
      <SeverityDrawer open={true} groups={null} loading={false} error={null} {...props} />
    </MemoryRouter>
  )
}

describe('SeverityDrawer', () => {
  it('no renderiza nada si open es false', () => {
    renderDrawer({ open: false })
    expect(screen.queryByTestId('severity-drawer')).not.toBeInTheDocument()
  })

  it('muestra "Cargando..." mientras loading es true', () => {
    renderDrawer({ loading: true })
    expect(screen.getByTestId('severity-drawer')).toHaveTextContent('Cargando...')
  })

  it('muestra un mensaje de error', () => {
    renderDrawer({ error: 'boom' })
    expect(screen.getByText('Error al cargar.')).toBeInTheDocument()
  })

  it('muestra mensaje cuando no hay grupos', () => {
    renderDrawer({ groups: [] })
    expect(screen.getByText('No hay riesgos ni issues para mostrar.')).toBeInTheDocument()
  })

  it('renderiza grupos por severidad con links a riesgos e issues', () => {
    renderDrawer({
      groups: [
        {
          severity: 1,
          items: [
            { id: 'r1', title: 'Riesgo crítico', status: 'open', type: 'risk' },
            { id: 'i1', title: 'Issue crítico', status: 'closed', type: 'issue' },
          ],
        },
        {
          severity: 3,
          items: [
            { id: 'r2', title: 'Riesgo medio', status: 'in_progress', type: 'risk' },
          ],
        },
      ],
    })

    expect(screen.getByTestId('severity-group-1')).toBeInTheDocument()
    expect(screen.getByTestId('severity-group-3')).toBeInTheDocument()

    const riskLink = screen.getByRole('link', { name: /Riesgo crítico/ })
    expect(riskLink).toHaveAttribute('href', '/risks/r1')

    const issueLink = screen.getByRole('link', { name: /Issue crítico/ })
    expect(issueLink).toHaveAttribute('href', '/issues/i1')

    expect(screen.getAllByTestId('severity-badge')).toHaveLength(2)
  })
})
