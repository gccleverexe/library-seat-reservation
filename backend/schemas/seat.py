from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class SeatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seat_number: str
    floor: int
    area: str
    description: Optional[str]
    status: str
    created_at: datetime


class SeatListQuery(BaseModel):
    floor: Optional[int] = None
    area: Optional[str] = None
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None


class SeatCreate(BaseModel):
    seat_number: str
    floor: int
    area: str
    description: Optional[str] = None


class SeatUpdate(BaseModel):
    seat_number: Optional[str] = None
    floor: Optional[int] = None
    area: Optional[str] = None
    description: Optional[str] = None


VALID_STATUSES = {"available", "reserved", "occupied", "unavailable"}


class SeatStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(sorted(VALID_STATUSES))}")
        return v
