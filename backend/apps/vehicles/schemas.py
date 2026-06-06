from ninja import Schema
from datetime import datetime
from typing import Optional
from pydantic import Field


class VehicleIn(Schema):
    code: str
    model: str
    capacity: int = Field(..., gt=0, description='承载容量必须大于0')
    current_load: int = Field(0, ge=0, description='当前装载量不能为负数')
    status: str = 'active'
    driver: Optional[str] = None


class VehicleOut(Schema):
    id: int
    code: str
    model: str
    capacity: int
    current_load: int
    status: str
    driver: Optional[str] = None
    created_at: datetime
    updated_at: datetime
