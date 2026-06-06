import request from '@/utils/request'

export interface TourTaskParams {
  status?: string
  program_id?: number | string
  city?: string
  keyword?: string
}

export interface TourTaskPropItem {
  prop_id: number | string
  quantity: number
}

export interface TourTaskPayload {
  program_id: number | string
  performance_date: string
  city: string
  venue: string
  person_in_charge: string
  start_date: string
  end_date: string
  remark?: string
  vehicle_ids: (number | string)[]
  props: TourTaskPropItem[]
}

export interface TourTaskStatusPayload {
  status: string
  execution_status?: string
  abnormal_situation?: string
  completion_result?: string
}

export function getTourTasks(params?: TourTaskParams) {
  return request.get('/tours/list', { params })
}

export function getTourTask(id: number | string) {
  return request.get(`/tours/${id}`)
}

export function createTourTask(data: TourTaskPayload) {
  return request.post('/tours/list', data)
}

export function updateTourTask(id: number | string, data: TourTaskPayload) {
  return request.put(`/tours/${id}`, data)
}

export function updateTourTaskStatus(id: number | string, data: TourTaskStatusPayload) {
  return request.post(`/tours/${id}/status`, data)
}

export function deleteTourTask(id: number | string) {
  return request.delete(`/tours/${id}`)
}

export function getTourTaskStats() {
  return request.get('/tours/stats')
}

export function getScheduleRank() {
  return request.get('/tours/schedule-rank')
}
