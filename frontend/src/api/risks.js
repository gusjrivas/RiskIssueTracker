import { apiGet, apiPost, apiPatch, apiDelete } from './client'

export const getRisks = (params = {}) => {
  const qs = new URLSearchParams({ page: 1, size: 50, ...params }).toString()
  return apiGet(`/api/v1/risks?${qs}`)
}

export const getRisk = (id) => apiGet(`/api/v1/risks/${id}`)

export const createRisk = (data) => apiPost('/api/v1/risks', data)

export const updateRisk = (id, data) => apiPatch(`/api/v1/risks/${id}`, data)

export const deleteRisk = (id) => apiDelete(`/api/v1/risks/${id}`)

export const transitionRiskStatus = (id, status) =>
  apiPatch(`/api/v1/risks/${id}/status`, { status })

export const getRiskHistory = (id) => apiGet(`/api/v1/history/risk/${id}`)
