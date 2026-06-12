import { apiGet } from './client'

export const getDashboardStats = () => apiGet('/api/v1/dashboard/stats')
