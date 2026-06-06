import request from '@/utils/request'

export interface VehicleParams {
  status?: string
}

export function getVehicles(params?: VehicleParams) {
  return request.get('/vehicles', { params })
}

export function getVehicle(id: number | string) {
  return request.get(`/vehicles/${id}`)
}

export function createVehicle(data: any) {
  return request.post('/vehicles', data)
}

export function updateVehicle(id: number | string, data: any) {
  return request.put(`/vehicles/${id}`, data)
}

export function deleteVehicle(id: number | string) {
  return request.delete(`/vehicles/${id}`)
}
