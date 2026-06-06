import request from '@/utils/request'
import type {
  TourCostItemPayload,
  TourCostItemUpdatePayload,
  TourSettlementPayload,
  TourSettlementSubmitPayload
} from '@/types'

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

export interface TourCostItemParams {
  tour_task_id?: number | string
  cost_type?: string
  program_id?: number | string
  city?: string
  start_date?: string
  end_date?: string
}

export interface TourSettlementParams {
  tour_task_id?: number | string
  settlement_status?: string
  program_id?: number | string
  city?: string
  start_date?: string
  end_date?: string
}

export interface TourCostStatsParams {
  program_id?: number | string
  city?: string
  start_date?: string
  end_date?: string
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

export function getCostItems(params?: TourCostItemParams) {
  return request.get('/tours/cost-items', { params })
}

export function getCostItem(id: number | string) {
  return request.get(`/tours/cost-items/${id}`)
}

export function createCostItem(data: TourCostItemPayload) {
  return request.post('/tours/cost-items', data)
}

export function updateCostItem(id: number | string, data: TourCostItemUpdatePayload) {
  return request.put(`/tours/cost-items/${id}`, data)
}

export function deleteCostItem(id: number | string) {
  return request.delete(`/tours/cost-items/${id}`)
}

export function getSettlements(params?: TourSettlementParams) {
  return request.get('/tours/settlements', { params })
}

export function getSettlement(id: number | string) {
  return request.get(`/tours/settlements/${id}`)
}

export function createSettlement(data: TourSettlementPayload) {
  return request.post('/tours/settlements', data)
}

export function refreshSettlement(id: number | string) {
  return request.post(`/tours/settlements/${id}/refresh`)
}

export function submitSettlement(id: number | string, data: TourSettlementSubmitPayload) {
  return request.post(`/tours/settlements/${id}/submit`, data)
}

export function confirmSettlement(id: number | string) {
  return request.post(`/tours/settlements/${id}/confirm`)
}

export function deleteSettlement(id: number | string) {
  return request.delete(`/tours/settlements/${id}`)
}

export function getCostStatsSummary(params?: TourCostStatsParams) {
  return request.get('/tours/cost-stats/summary', { params })
}

export function getCostStatsByProgram(params?: { start_date?: string; end_date?: string }) {
  return request.get('/tours/cost-stats/by-program', { params })
}

export function getCostStatsByCity(params?: { start_date?: string; end_date?: string }) {
  return request.get('/tours/cost-stats/by-city', { params })
}
