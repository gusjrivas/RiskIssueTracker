import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import StatusBadge from '../../components/StatusBadge'

describe('StatusBadge', () => {
  it('renderiza la etiqueta para open', () => {
    render(<StatusBadge status="open" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Abierto')
  })

  it('renderiza la etiqueta para in_progress', () => {
    render(<StatusBadge status="in_progress" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('En progreso')
  })

  it('renderiza la etiqueta para closed', () => {
    render(<StatusBadge status="closed" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Cerrado')
  })

  it('renderiza la etiqueta para derived', () => {
    render(<StatusBadge status="derived" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Derivado')
  })

  it('renderiza la etiqueta para pending', () => {
    render(<StatusBadge status="pending" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Pendiente')
  })

  it('renderiza la etiqueta para active', () => {
    render(<StatusBadge status="active" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Activo')
  })

  it('renderiza la etiqueta para inactive', () => {
    render(<StatusBadge status="inactive" />)
    expect(screen.getByTestId('status-badge')).toHaveTextContent('Inactivo')
  })

  it('open tiene clase de acento azul', () => {
    render(<StatusBadge status="open" />)
    expect(screen.getByTestId('status-badge').className).toContain('text-accent')
  })

  it('closed tiene clase verde', () => {
    render(<StatusBadge status="closed" />)
    expect(screen.getByTestId('status-badge').className).toContain('text-severity-green')
  })

  it('inactive tiene clase roja', () => {
    render(<StatusBadge status="inactive" />)
    expect(screen.getByTestId('status-badge').className).toContain('text-severity-red')
  })
})
