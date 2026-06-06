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

export interface DashboardData {
  vehicle_load_rates: VehicleLoadRate[]
  program_prop_dist: ProgramPropDist[]
  tour_flow_stats: TourFlowStats
  maintenance_stats: MaintenanceStats
  high_loss_programs: HighLossProgram[]
  tour_task_stats: TourTaskStats
  program_schedule_rank: ProgramScheduleRank[]
}
