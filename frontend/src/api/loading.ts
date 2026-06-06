import request from '@/utils/request'

export function getLoadingList() {
  return request.get('/loading/list')
}

export function createLoading(data: any) {
  return request.post('/loading/list', data)
}

export function getLoading(id: number | string) {
  return request.get(`/loading/${id}`)
}

export function updateLoading(id: number | string, data: any) {
  return request.put(`/loading/${id}`, data)
}

export function deleteLoading(id: number | string) {
  return request.delete(`/loading/${id}`)
}

export function getUnloadingList() {
  return request.get('/unloading/list')
}

export function createUnloading(data: any) {
  return request.post('/unloading/list', data)
}

export function getUnloading(id: number | string) {
  return request.get(`/unloading/${id}`)
}

export function updateUnloading(id: number | string, data: any) {
  return request.put(`/unloading/${id}`, data)
}

export function deleteUnloading(id: number | string) {
  return request.delete(`/unloading/${id}`)
}

export function getDamageList() {
  return request.get('/damage/list')
}

export function createDamage(data: any) {
  return request.post('/damage/list', data)
}

export function getDamage(id: number | string) {
  return request.get(`/damage/${id}`)
}

export function updateDamage(id: number | string, data: any) {
  return request.put(`/damage/${id}`, data)
}

export function deleteDamage(id: number | string) {
  return request.delete(`/damage/${id}`)
}
