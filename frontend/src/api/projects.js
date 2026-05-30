import { apiGet, apiPost, apiPatch, apiDelete } from './client'

export const getProjects = (page = 1, size = 20) =>
  apiGet(`/api/v1/projects?page=${page}&size=${size}`)

export const getProject = (id) => apiGet(`/api/v1/projects/${id}`)

export const createProject = (data) => apiPost('/api/v1/projects', data)

export const updateProject = (id, data) => apiPatch(`/api/v1/projects/${id}`, data)

export const deleteProject = (id) => apiDelete(`/api/v1/projects/${id}`)
