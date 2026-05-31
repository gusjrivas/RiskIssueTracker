import { apiGet, apiPatch } from './client'

export const getUsers = (page = 1, size = 50) =>
  apiGet(`/api/v1/admin/users?page=${page}&size=${size}`)

export const approveUser = (userId) =>
  apiPatch(`/api/v1/admin/users/${userId}/approve`)

export const deactivateUser = (userId) =>
  apiPatch(`/api/v1/admin/users/${userId}/deactivate`)

export const updateUser = (userId, data) =>
  apiPatch(`/api/v1/admin/users/${userId}`, data)
