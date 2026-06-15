import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useSeverityGroups } from '../../hooks/useSeverityGroups'
import * as dashboardApi from '../../api/dashboard'

vi.mock('../../api/dashboard')

describe('useSeverityGroups', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('no hace fetch hasta que se llama fetchGroups', () => {
    dashboardApi.getSeverityGroups.mockResolvedValue({ groups: [] })
    renderHook(() => useSeverityGroups())

    expect(dashboardApi.getSeverityGroups).not.toHaveBeenCalled()
  })

  it('carga los groups y los expone en data', async () => {
    const groups = [{ severity: 1, items: [{ id: 'r1', title: 'Risk 1', status: 'open', type: 'risk' }] }]
    dashboardApi.getSeverityGroups.mockResolvedValue({ groups })
    const { result } = renderHook(() => useSeverityGroups())

    await act(async () => {
      await result.current.fetchGroups()
    })

    expect(result.current.data).toEqual(groups)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
  })

  it('no vuelve a pedir datos si fetchGroups se llama de nuevo (cache)', async () => {
    dashboardApi.getSeverityGroups.mockResolvedValue({ groups: [] })
    const { result } = renderHook(() => useSeverityGroups())

    await act(async () => {
      await result.current.fetchGroups()
    })
    await act(async () => {
      await result.current.fetchGroups()
    })

    expect(dashboardApi.getSeverityGroups).toHaveBeenCalledTimes(1)
  })

  it('expone error si la API falla y permite reintentar', async () => {
    dashboardApi.getSeverityGroups.mockRejectedValueOnce(new Error('boom'))
    dashboardApi.getSeverityGroups.mockResolvedValueOnce({ groups: [] })
    const { result } = renderHook(() => useSeverityGroups())

    await act(async () => {
      await result.current.fetchGroups()
    })
    expect(result.current.error).toBe('boom')
    expect(result.current.loading).toBe(false)

    await act(async () => {
      await result.current.fetchGroups()
    })
    expect(dashboardApi.getSeverityGroups).toHaveBeenCalledTimes(2)
    expect(result.current.error).toBeNull()
    expect(result.current.data).toEqual([])
  })
})
