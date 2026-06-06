import request from '@/utils/request'

export interface PropParams {
  keyword?: string
  program_id?: number | string
  status?: string
  maintenance_status?: string
  scrap_status?: string
}

export function getProps(params?: PropParams) {
  return request.get('/props', { params })
}

export function getProp(id: number | string) {
  return request.get(`/props/${id}`)
}

export function createProp(data: any) {
  return request.post('/props', data)
}

export function updateProp(id: number | string, data: any) {
  return request.put(`/props/${id}`, data)
}

export function deleteProp(id: number | string) {
  return request.delete(`/props/${id}`)
}

export function getMaintenanceRecords(prop_id?: number | string) {
  const params: any = {}
  if (prop_id) params.prop_id = prop_id
  return request.get('/maintenance/list', { params })
}

export function createMaintenanceRecord(data: any) {
  return request.post('/maintenance/list', data)
}

export function updateMaintenanceRecord(id: number | string, data: any) {
  return request.put(`/maintenance/${id}`, data)
}

export function deleteMaintenanceRecord(id: number | string) {
  return request.delete(`/maintenance/${id}`)
}

export function getScrapApplications(prop_id?: number | string, status?: string) {
  const params: any = {}
  if (prop_id) params.prop_id = prop_id
  if (status) params.status = status
  return request.get('/scrap/list', { params })
}

export function createScrapApplication(data: any) {
  return request.post('/scrap/list', data)
}

export function approveScrapApplication(id: number | string, data: any) {
  return request.post(`/scrap/${id}/approve`, data)
}

export function rejectScrapApplication(id: number | string, data: any) {
  return request.post(`/scrap/${id}/reject`, data)
}

export function deleteScrapApplication(id: number | string) {
  return request.delete(`/scrap/${id}`)
}
