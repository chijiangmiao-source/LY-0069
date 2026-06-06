from typing import Optional, List
from ninja import Schema
from datetime import datetime, date
from decimal import Decimal


class PropIn(Schema):
    code: str
    name: str
    program_id: int
    material: Optional[str] = None
    status: str = 'in_store'
    location: Optional[str] = None
    maintenance_cycle_days: int = 90
    last_maintenance_date: Optional[date] = None
    maintenance_status: str = 'normal'
    scrap_status: str = 'active'


class PropOut(Schema):
    id: int
    code: str
    name: str
    program_id: int
    program_name: str
    material: Optional[str] = None
    status: str
    location: Optional[str] = None
    maintenance_cycle_days: int
    last_maintenance_date: Optional[date] = None
    next_maintenance_date: Optional[date] = None
    maintenance_status: str
    scrap_status: str
    created_at: datetime
    updated_at: datetime


class PropFilter(Schema):
    keyword: Optional[str] = None
    program_id: Optional[int] = None
    status: Optional[str] = None
    maintenance_status: Optional[str] = None
    scrap_status: Optional[str] = None


class MaintenanceRecordIn(Schema):
    prop_id: int
    type: str
    maintenance_date: date
    description: str
    operator: str
    result: str = 'pending'
    cost: Decimal = Decimal('0')
    remark: Optional[str] = None


class MaintenanceRecordOut(Schema):
    id: int
    prop_id: int
    prop_code: str
    prop_name: str
    type: str
    maintenance_date: date
    description: str
    operator: str
    result: str
    cost: Decimal
    remark: Optional[str] = None
    created_at: datetime


class ScrapApplicationIn(Schema):
    prop_id: int
    applicant: str
    apply_date: date
    reason: str


class ScrapApplicationApprove(Schema):
    approver: str
    approve_date: date
    approve_remark: Optional[str] = None


class ScrapApplicationOut(Schema):
    id: int
    prop_id: int
    prop_code: str
    prop_name: str
    applicant: str
    apply_date: date
    reason: str
    status: str
    approver: Optional[str] = None
    approve_date: Optional[date] = None
    approve_remark: Optional[str] = None
    created_at: datetime
