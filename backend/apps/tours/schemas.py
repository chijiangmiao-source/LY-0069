from typing import Optional, List
from ninja import Schema
from datetime import datetime, date
from pydantic import Field


class TourTaskVehicleIn(Schema):
    vehicle_id: int


class TourTaskVehicleOut(Schema):
    id: int
    vehicle_id: int
    vehicle_code: str
    vehicle_model: str


class TourTaskPropIn(Schema):
    prop_id: int
    quantity: int = Field(1, gt=0)


class TourTaskPropOut(Schema):
    id: int
    prop_id: int
    prop_code: str
    prop_name: str
    quantity: int


class TourTaskIn(Schema):
    program_id: int
    performance_date: date
    city: str
    venue: str
    person_in_charge: str
    start_date: date
    end_date: date
    remark: Optional[str] = None
    vehicle_ids: List[int] = []
    props: List[TourTaskPropIn] = []


class TourTaskUpdateIn(Schema):
    program_id: int
    performance_date: date
    city: str
    venue: str
    person_in_charge: str
    start_date: date
    end_date: date
    remark: Optional[str] = None
    vehicle_ids: List[int] = []
    props: List[TourTaskPropIn] = []


class TourTaskStatusUpdate(Schema):
    status: str
    execution_status: Optional[str] = None
    abnormal_situation: Optional[str] = None
    completion_result: Optional[str] = None


class TourTaskOut(Schema):
    id: int
    program_id: int
    program_name: str
    performance_date: date
    city: str
    venue: str
    person_in_charge: str
    start_date: date
    end_date: date
    status: str
    execution_status: str
    abnormal_situation: Optional[str] = None
    completion_result: Optional[str] = None
    remark: Optional[str] = None
    vehicles: List[TourTaskVehicleOut] = []
    props: List[TourTaskPropOut] = []
    created_at: datetime
    updated_at: datetime


class TourTaskStats(Schema):
    future_tasks_count: int
    in_progress_tasks_count: int
    abnormal_tasks_count: int


class ProgramScheduleRank(Schema):
    program_name: str
    task_count: int
    upcoming_count: int


class TourCostItemIn(Schema):
    tour_task_id: int
    cost_type: str
    amount: float
    description: Optional[str] = None
    expense_date: date
    operator: Optional[str] = None
    receipt_no: Optional[str] = None
    is_abnormal_cost: bool = False
    abnormal_remark: Optional[str] = None


class TourCostItemUpdate(Schema):
    cost_type: str
    amount: float
    description: Optional[str] = None
    expense_date: date
    operator: Optional[str] = None
    receipt_no: Optional[str] = None
    is_abnormal_cost: bool = False
    abnormal_remark: Optional[str] = None


class TourCostItemOut(Schema):
    id: int
    tour_task_id: int
    tour_task_name: str
    cost_type: str
    cost_type_display: str
    amount: float
    description: Optional[str] = None
    expense_date: date
    operator: Optional[str] = None
    receipt_no: Optional[str] = None
    is_abnormal_cost: bool
    abnormal_remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TourSettlementIn(Schema):
    tour_task_id: int
    remark: Optional[str] = None


class TourSettlementSubmit(Schema):
    abnormal_cost_note: Optional[str] = None
    remark: Optional[str] = None


class TourSettlementOut(Schema):
    id: int
    tour_task_id: int
    tour_task_name: str
    program_name: str
    city: str
    performance_date: date
    task_status: str
    settlement_no: str
    transport_cost: float
    labor_cost: float
    venue_cost: float
    maintenance_cost: float
    temporary_purchase_cost: float
    abnormal_handling_cost: float
    total_cost: float
    abnormal_cost_note: Optional[str] = None
    settlement_status: str
    settler: Optional[str] = None
    settlement_date: Optional[date] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TourCostStats(Schema):
    total_cost: float
    transport_cost: float
    labor_cost: float
    venue_cost: float
    maintenance_cost: float
    temporary_purchase_cost: float
    abnormal_handling_cost: float
    task_count: int
    avg_cost_per_task: float
    abnormal_cost_ratio: float


class ProgramCostRank(Schema):
    program_name: str
    total_cost: float
    task_count: int
    avg_cost_per_task: float


class CityCostStat(Schema):
    city: str
    total_cost: float
    task_count: int
    avg_cost_per_task: float
