from ninja import Schema
from datetime import date, datetime
from typing import Optional
from pydantic import Field


class LoadingIn(Schema):
    vehicle_id: int
    prop_id: int
    loading_date: date
    loading_quantity: int = Field(1, gt=0, description='装车数量必须大于0')
    operator: str
    remark: Optional[str] = None


class LoadingOut(Schema):
    id: int
    vehicle_id: int
    vehicle_code: str
    prop_id: int
    prop_code: str
    prop_name: str
    loading_date: date
    loading_quantity: int
    operator: str
    remark: Optional[str] = None
    created_at: datetime


class UnloadingIn(Schema):
    loading_id: int
    vehicle_id: int
    prop_id: int
    unloading_date: date
    unloading_quantity: int = Field(..., gt=0, description='卸车数量必须大于0')
    operator: str
    remark: Optional[str] = None


class UnloadingOut(Schema):
    id: int
    loading_id: int
    vehicle_id: int
    vehicle_code: str
    prop_id: int
    prop_code: str
    prop_name: str
    unloading_date: date
    unloading_quantity: int
    operator: str
    remark: Optional[str] = None
    created_at: datetime


class DamageIn(Schema):
    prop_id: int
    damage_date: date
    damage_quantity: int = Field(..., gt=0, description='损耗数量必须大于0')
    damage_reason: str
    handler: str
    remark: Optional[str] = None


class DamageOut(Schema):
    id: int
    prop_id: int
    prop_code: str
    prop_name: str
    damage_date: date
    damage_quantity: int
    damage_reason: str
    handler: str
    remark: Optional[str] = None
    created_at: datetime
