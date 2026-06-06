import { apiGet } from './client'

export const getActiveUsers = () => apiGet('/api/v1/users?size=200')
