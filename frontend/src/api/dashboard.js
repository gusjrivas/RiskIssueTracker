import { apiGet } from './client'

export const getDashboardStats = () => apiGet('/api/v1/dashboard/stats')

export const getSeverityGroups = () =>
  apiGet('/api/v1/dashboard/stats/severity-items')
