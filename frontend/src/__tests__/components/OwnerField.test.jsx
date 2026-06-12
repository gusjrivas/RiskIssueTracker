import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import OwnerField from '../../components/OwnerField'

vi.mock('../../api/users', () => ({
  getActiveUsers: vi.fn().mockResolvedValue({
    items: [
      { id: 'user-1', full_name: 'Ana García', email: 'ana@test.com' },
      { id: 'user-2', full_name: 'Juan Pérez', email: 'juan@test.com' },
    ],
  }),
}))

describe('OwnerField', () => {
  it('muestra el nombre del responsable actual', async () => {
    render(<OwnerField ownerId="user-1" onSave={vi.fn()} />)
    expect(await screen.findByText('Ana García')).toBeInTheDocument()
  })

  it('con readOnly oculta el lápiz de edición', async () => {
    render(<OwnerField ownerId="user-1" onSave={vi.fn()} readOnly />)
    await screen.findByText('Ana García')
    expect(screen.queryByTitle('Cambiar responsable')).not.toBeInTheDocument()
  })

  describe('prop disabled', () => {
    it('muestra el lápiz pero deshabilitado', async () => {
      render(<OwnerField ownerId="user-1" onSave={vi.fn()} disabled />)
      await screen.findByText('Ana García')
      expect(screen.getByTitle('Cambiar responsable')).toBeDisabled()
    })
  })

  describe('errores del backend', () => {
    it('muestra el mensaje cuando guardar falla', async () => {
      const onSave = vi.fn().mockRejectedValue(new Error('Sin permiso para modificar este riesgo'))
      render(<OwnerField ownerId="user-1" onSave={onSave} />)
      await screen.findByText('Ana García')
      await userEvent.click(screen.getByTitle('Cambiar responsable'))
      await userEvent.click(screen.getByTitle('Guardar'))
      await waitFor(() =>
        expect(screen.getByText('Sin permiso para modificar este riesgo')).toBeInTheDocument()
      )
    })
  })
})
