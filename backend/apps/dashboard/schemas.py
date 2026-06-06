from ninja import Schema
from typing import List


class VehicleLoadRate(Schema):
    vehicle_code: str
    model: str
    capacity: int
    current_load: int
    load_rate: float


class ProgramPropDist(Schema):
    program_name: str
    prop_count: int


class TourFlowStats(Schema):
    total_loading_count: int
    total_unloading_count: int
    total_tour_count: int


class MaintenanceStats(Schema):
    maintenance_due_count: int
    maintenance_overdue_count: int
    scrap_proportion: float


class HighLossProgram(Schema):
    program_name: str
    total_damage_quantity: int
    prop_count: int


class TourTaskStats(Schema):
    future_tasks_count: int
    in_progress_tasks_count: int
    abnormal_tasks_count: int


class ProgramScheduleRank(Schema):
    program_name: str
    task_count: int
    upcoming_count: int


class DashboardData(Schema):
    vehicle_load_rates: List[VehicleLoadRate]
    program_prop_dist: List[ProgramPropDist]
    tour_flow_stats: TourFlowStats
    maintenance_stats: MaintenanceStats
    high_loss_programs: List[HighLossProgram]
    tour_task_stats: TourTaskStats
    program_schedule_rank: List[ProgramScheduleRank]
