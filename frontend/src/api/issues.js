import { apiGet, apiPost, apiPatch, apiDelete } from './client'

export const getIssues = (params = {}) => {
  const qs = new URLSearchParams({ page: 1, size: 50, ...params }).toString()
  return apiGet(`/api/v1/issues?${qs}`)
}

export const getIssue = (id) => apiGet(`/api/v1/issues/${id}`)

export const createIssue = (data) => apiPost('/api/v1/issues', data)

export const deriveIssue = (riskId) => apiPost('/api/v1/issues/derive', { risk_id: riskId })

export const updateIssue = (id, data) => apiPatch(`/api/v1/issues/${id}`, data)

export const deleteIssue = (id) => apiDelete(`/api/v1/issues/${id}`)

export const transitionIssueStatus = (id, status) =>
  apiPatch(`/api/v1/issues/${id}/status`, { status })

export const getIssueHistory = (id) => apiGet(`/api/v1/history/issue/${id}`)
