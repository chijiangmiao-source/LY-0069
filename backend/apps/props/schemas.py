from typing import Optional
from ninja import Schema
from datetime import datetime


class PropIn(Schema):
    code: str
    name: str
    program_id: int
    material: Optional[str] = None
    status: str = 'in_store'
    location: Optional[str] = None


class PropOut(Schema):
    id: int
    code: str
    name: str
    program_id: int
    program_name: str
    material: Optional[str] = None
    status: str
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PropFilter(Schema):
    keyword: Optional[str] = None
    program_id: Optional[int] = None
    status: Optional[str] = None
