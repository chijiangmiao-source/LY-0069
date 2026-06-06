import request from '@/utils/request'

export interface PropParams {
  keyword?: string
  program_id?: number | string
  status?: string
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
