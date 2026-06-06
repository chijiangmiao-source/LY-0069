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


class DashboardData(Schema):
    vehicle_load_rates: List[VehicleLoadRate]
    program_prop_dist: List[ProgramPropDist]
    tour_flow_stats: TourFlowStats
