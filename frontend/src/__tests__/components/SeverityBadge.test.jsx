import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import SeverityBadge from '../../components/SeverityBadge'

// Tests escritos antes de implementar el componente (TDD)
describe('SeverityBadge', () => {
  describe('colores por zona de severidad', () => {
    it('muestra rojo para severidad 1 (crítico)', () => {
      render(<SeverityBadge severity={1} />)
      expect(screen.getByTestId('severity-badge')).toHaveClass('severity-red')
    })

    it('muestra rojo para severidad 3 (límite superior zona roja)', () => {
      render(<SeverityBadge severity={3} />)
      expect(screen.getByTestId('severity-badge')).toHaveClass('severity-red')
    })

    it('muestra amarillo para severidad 4 (límite inferior zona amarilla)', () => {
      render(<SeverityBadge severity={4} />)
      expect(screen.getByTestId('severity-badge')).toHaveClass('severity-yellow')
    })

    it('muestra amarillo para severidad 6 (límite superior zona amarilla)', () => {
      render(<SeverityBadge severity={6} />)
      expect(screen.getByTestId('severity-badge')).toHaveClass('severity-yellow')
    })

    it('muestra verde para severidad 7 (límite inferior zona verde)', () => {
      render(<SeverityBadge severity={7} />)
      expect(screen.getByTestId('severity-badge')).toHaveClass('severity-green')
    })

    it('muestra verde para severidad 9 (mínimo impacto)', () => {
      render(<SeverityBadge severity={9} />)
      expect(screen.getByTestId('severity-badge')).toHaveClass('severity-green')
    })
  })

  describe('etiqueta de texto', () => {
    it('muestra el número de severidad', () => {
      render(<SeverityBadge severity={1} />)
      expect(screen.getByTestId('severity-badge')).toHaveTextContent('1')
    })

    it('acepta severidad como número', () => {
      render(<SeverityBadge severity={5} />)
      expect(screen.getByTestId('severity-badge')).toBeInTheDocument()
    })
  })
})
