from datetime import datetime
from ninja import Schema
from typing import Optional


class ProgramIn(Schema):
    name: str
    description: Optional[str] = None


class ProgramOut(Schema):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
