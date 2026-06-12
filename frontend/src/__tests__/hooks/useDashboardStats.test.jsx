import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useDashboardStats } from '../../hooks/useDashboardStats'
import * as dashboardApi from '../../api/dashboard'

vi.mock('../../api/dashboard')

const STATS = {
  risks: { total: 2, by_severity: { 1: 2 }, by_status: { open: 2 } },
  issues: { total: 0, by_severity: {}, by_status: {} },
}

describe('useDashboardStats', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('carga las stats y expone data con loading en false', async () => {
    dashboardApi.getDashboardStats.mockResolvedValue(STATS)
    const { result } = renderHook(() => useDashboardStats())
    expect(result.current.loading).toBe(true)
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data).toEqual(STATS)
    expect(result.current.error).toBeNull()
  })

  it('expone error si la API falla', async () => {
    dashboardApi.getDashboardStats.mockRejectedValue(new Error('boom'))
    const { result } = renderHook(() => useDashboardStats())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBe('boom')
    expect(result.current.data).toBeNull()
  })

  it('refetch vuelve a llamar a la API', async () => {
    dashboardApi.getDashboardStats.mockResolvedValue(STATS)
    const { result } = renderHook(() => useDashboardStats())
    await waitFor(() => expect(result.current.loading).toBe(false))
    await result.current.refetch()
    expect(dashboardApi.getDashboardStats).toHaveBeenCalledTimes(2)
  })
})
