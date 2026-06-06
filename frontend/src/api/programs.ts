import request from '@/utils/request'

export function getPrograms(params?: any) {
  return request.get('/programs', { params })
}

export function getProgram(id: number | string) {
  return request.get(`/programs/${id}`)
}

export function createProgram(data: any) {
  return request.post('/programs', data)
}

export function updateProgram(id: number | string, data: any) {
  return request.put(`/programs/${id}`, data)
}

export function deleteProgram(id: number | string) {
  return request.delete(`/programs/${id}`)
}
