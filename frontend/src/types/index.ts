export interface User {
  id: number
  username: string
  role: string
  token: string
}

export interface Program {
  id: number
  name: string
  description: string
  created_at: string
  updated_at: string
}

export interface Prop {
  id: number
  code: string
  name: string
  program_id: number
  program_name?: string
  material: string
  status: string
  location: string
  maintenance_cycle_days: number
  last_maintenance_date?: string
  next_maintenance_date?: string
  maintenance_status: string
  scrap_status: string
  created_at: string
  updated_at: string
}

export interface MaintenanceRecord {
  id: number
  prop_id: number
  prop_code?: string
  prop_name?: string
  type: string
  maintenance_date: string
  description: string
  operator: string
  result: string
  cost: number
  remark?: string
  created_at: string
}

export interface ScrapApplication {
  id: number
  prop_id: number
  prop_code?: string
  prop_name?: string
  applicant: string
  apply_date: string
  reason: string
  status: string
  approver?: string
  approve_date?: string
  approve_remark?: string
  created_at: string
}

export interface Vehicle {
  id: number
  code: string
  model: string
  capacity: number
  current_load: number
  status: string
  driver: string
  created_at: string
  updated_at: string
}

export interface LoadingRecord {
  id: number
  vehicle_id: number
  vehicle_code?: string
  prop_id: number
  prop_code?: string
  loading_date: string
  loading_quantity: number
  operator: string
  remark: string
  created_at: string
}

export interface UnloadingRecord {
  id: number
  loading_id: number
  vehicle_id: number
  vehicle_code?: string
  prop_id: number
  prop_code?: string
  unloading_date: string
  unloading_quantity: number
  operator: string
  remark: string
  created_at: string
}

export interface DamageRecord {
  id: number
  prop_id: number
  prop_code?: string
  damage_date: string
  damage_quantity: number
  damage_reason: string
  handler: string
  remark: string
  created_at: string
}

export interface VehicleLoadRate {
  vehicle_code: string
  model: string
  capacity: number
  current_load: number
  load_rate: number
}

export interface ProgramPropDist {
  program_name: string
  prop_count: number
}

export interface TourFlowStats {
  total_loading_count: number
  total_unloading_count: number
  total_tour_count: number
}

export interface MaintenanceStats {
  maintenance_due_count: number
  maintenance_overdue_count: number
  scrap_proportion: number
}

export interface HighLossProgram {
  program_name: string
  total_damage_quantity: number
  prop_count: number
}

export interface TourTaskVehicle {
  id: number
  vehicle_id: number
  vehicle_code: string
  vehicle_model: string
}

export interface TourTaskProp {
  id: number
  prop_id: number
  prop_code: string
  prop_name: string
  quantity: number
}

export interface TourTask {
  id: number
  program_id: number
  program_name: string
  performance_date: string
  city: string
  venue: string
  person_in_charge: string
  start_date: string
  end_date: string
  status: string
  execution_status: string
  abnormal_situation?: string
  completion_result?: string
  remark?: string
  vehicles: TourTaskVehicle[]
  props: TourTaskProp[]
  created_at: string
  updated_at: string
}

export interface TourTaskStats {
  future_tasks_count: number
  in_progress_tasks_count: number
  abnormal_tasks_count: number
}

export interface ProgramScheduleRank {
  program_name: string
  task_count: number
  upcoming_count: number
}

export interface TourCostItem {
  id: number
  tour_task_id: number
  tour_task_name: string
  cost_type: string
  cost_type_display: string
  amount: number
  description?: string
  expense_date: string
  operator?: string
  receipt_no?: string
  is_abnormal_cost: boolean
  abnormal_remark?: string
  created_at: string
  updated_at: string
}

export interface TourCostItemPayload {
  tour_task_id: number | string
  cost_type: string
  amount: number
  description?: string
  expense_date: string
  operator?: string
  receipt_no?: string
  is_abnormal_cost?: boolean
  abnormal_remark?: string
}

export interface TourCostItemUpdatePayload {
  cost_type: string
  amount: number
  description?: string
  expense_date: string
  operator?: string
  receipt_no?: string
  is_abnormal_cost?: boolean
  abnormal_remark?: string
}

export interface TourSettlement {
  id: number
  tour_task_id: number
  tour_task_name: string
  program_name: string
  city: string
  performance_date: string
  task_status: string
  settlement_no: string
  transport_cost: number
  labor_cost: number
  venue_cost: number
  maintenance_cost: number
  temporary_purchase_cost: number
  abnormal_handling_cost: number
  total_cost: number
  abnormal_cost_note?: string
  settlement_status: string
  settler?: string
  settlement_date?: string
  remark?: string
  created_at: string
  updated_at: string
}

export interface TourSettlementPayload {
  tour_task_id: number | string
  remark?: string
}

export interface TourSettlementSubmitPayload {
  abnormal_cost_note?: string
  remark?: string
}

export interface TourCostStats {
  total_cost: number
  transport_cost: number
  labor_cost: number
  venue_cost: number
  maintenance_cost: number
  temporary_purchase_cost: number
  abnormal_handling_cost: number
  task_count: number
  avg_cost_per_task: number
  abnormal_cost_ratio: number
}

export interface ProgramCostRank {
  program_name: string
  total_cost: number
  task_count: number
  avg_cost_per_task: number
}

export interface CityCostStat {
  city: string
  total_cost: number
  task_count: number
  avg_cost_per_task: number
}

export interface DashboardData {
  vehicle_load_rates: VehicleLoadRate[]
  program_prop_dist: ProgramPropDist[]
  tour_flow_stats: TourFlowStats
  maintenance_stats: MaintenanceStats
  high_loss_programs: HighLossProgram[]
  tour_task_stats: TourTaskStats
  program_schedule_rank: ProgramScheduleRank[]
  tour_cost_stats: TourCostStats
  program_cost_rank: ProgramCostRank[]
}
