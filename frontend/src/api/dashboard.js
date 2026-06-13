import { apiGet } from './client'

export const getDashboardStats = () => apiGet('/api/v1/dashboard/stats')

export const getSeverityItems = (severity, type) =>
  apiGet(`/api/v1/dashboard/stats/severity/${severity}?type=${type}`)
