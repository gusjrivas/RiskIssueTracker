import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useSeverityItems } from '../../hooks/useSeverityItems'
import * as dashboardApi from '../../api/dashboard'

vi.mock('../../api/dashboard')

describe('useSeverityItems', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('carga items para severity+type y los expone en itemsByKey', async () => {
    dashboardApi.getSeverityItems.mockResolvedValue({
      items: [{ id: '1', title: 'Risk 1', status: 'open' }],
    })
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(1, 'risk')
    })

    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'risk')
    expect(result.current.itemsByKey['1-risk']).toEqual([
      { id: '1', title: 'Risk 1', status: 'open' },
    ])
    expect(result.current.loadingByKey['1-risk']).toBe(false)
  })

  it('no vuelve a pedir datos para la misma severity+type (cache)', async () => {
    dashboardApi.getSeverityItems.mockResolvedValue({ items: [] })
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(2, 'issue')
    })
    await act(async () => {
      await result.current.fetchItems(2, 'issue')
    })

    expect(dashboardApi.getSeverityItems).toHaveBeenCalledTimes(1)
  })

  it('cachea por separado severity+type distintos', async () => {
    dashboardApi.getSeverityItems.mockResolvedValue({ items: [] })
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(1, 'risk')
    })
    await act(async () => {
      await result.current.fetchItems(1, 'issue')
    })

    expect(dashboardApi.getSeverityItems).toHaveBeenCalledTimes(2)
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'risk')
    expect(dashboardApi.getSeverityItems).toHaveBeenCalledWith(1, 'issue')
  })

  it('expone error si la API falla', async () => {
    dashboardApi.getSeverityItems.mockRejectedValue(new Error('boom'))
    const { result } = renderHook(() => useSeverityItems())

    await act(async () => {
      await result.current.fetchItems(3, 'risk')
    })

    expect(result.current.errorByKey['3-risk']).toBe('boom')
    expect(result.current.loadingByKey['3-risk']).toBe(false)
    expect(result.current.itemsByKey['3-risk']).toBeUndefined()
  })
})
