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
  created_at: string
  updated_at: string
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

export interface DashboardData {
  vehicle_load_rates: VehicleLoadRate[]
  program_prop_dist: ProgramPropDist[]
  tour_flow_stats: TourFlowStats
}
