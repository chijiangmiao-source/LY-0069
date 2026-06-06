from ninja import Schema
from datetime import datetime
from typing import Optional


class VehicleIn(Schema):
    code: str
    model: str
    capacity: int
    current_load: int = 0
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
