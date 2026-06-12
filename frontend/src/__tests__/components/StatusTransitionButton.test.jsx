import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import StatusTransitionButton from '../../components/StatusTransitionButton'

describe('StatusTransitionButton', () => {
  it('muestra el botón de la siguiente transición', () => {
    render(<StatusTransitionButton currentStatus="open" onTransition={vi.fn()} />)
    expect(screen.getByRole('button', { name: /Iniciar/ })).toBeInTheDocument()
  })

  it('llama onTransition con el siguiente estado', async () => {
    const onTransition = vi.fn().mockResolvedValue()
    render(<StatusTransitionButton currentStatus="open" onTransition={onTransition} />)
    await userEvent.click(screen.getByRole('button', { name: /Iniciar/ }))
    expect(onTransition).toHaveBeenCalledWith('in_progress')
  })

  describe('prop disabled', () => {
    it('deshabilita el botón de transición', () => {
      render(<StatusTransitionButton currentStatus="open" onTransition={vi.fn()} disabled />)
      expect(screen.getByRole('button', { name: /Iniciar/ })).toBeDisabled()
    })

    it('deshabilita también las acciones extra', () => {
      render(
        <StatusTransitionButton
          currentStatus="in_progress"
          onTransition={vi.fn()}
          extraActions={[{ label: 'Derivar', status: 'derived' }]}
          disabled
        />
      )
      expect(screen.getByRole('button', { name: /Derivar/ })).toBeDisabled()
    })

    it('no llama onTransition si está deshabilitado', async () => {
      const onTransition = vi.fn()
      render(<StatusTransitionButton currentStatus="open" onTransition={onTransition} disabled />)
      await userEvent.click(screen.getByRole('button', { name: /Iniciar/ })).catch(() => {})
      expect(onTransition).not.toHaveBeenCalled()
    })
  })

  describe('errores del backend', () => {
    it('muestra el mensaje cuando la transición falla', async () => {
      const onTransition = vi.fn().mockRejectedValue(
        new Error('Sin permiso para cambiar el estado de este riesgo')
      )
      render(<StatusTransitionButton currentStatus="open" onTransition={onTransition} />)
      await userEvent.click(screen.getByRole('button', { name: /Iniciar/ }))
      await waitFor(() =>
        expect(screen.getByText('Sin permiso para cambiar el estado de este riesgo')).toBeInTheDocument()
      )
    })

    it('limpia el error en un reintento exitoso', async () => {
      const onTransition = vi.fn()
        .mockRejectedValueOnce(new Error('falló'))
        .mockResolvedValueOnce()
      render(<StatusTransitionButton currentStatus="open" onTransition={onTransition} />)
      await userEvent.click(screen.getByRole('button', { name: /Iniciar/ }))
      await waitFor(() => expect(screen.getByText('falló')).toBeInTheDocument())
      await userEvent.click(screen.getByRole('button', { name: /Iniciar/ }))
      await waitFor(() => expect(screen.queryByText('falló')).not.toBeInTheDocument())
    })
  })
})
