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
