import { apiGet } from './client'

export const getRiskActivity = (riskId) => apiGet(`/api/v1/risks/${riskId}/audit?size=50`)
export const getIssueActivity = (issueId) => apiGet(`/api/v1/issues/${issueId}/audit?size=50`)
