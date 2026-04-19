from typing import Dict

from pydantic import BaseModel


class SummaryOut(BaseModel):
    total_reservations: int
    completed_count: int
    cancelled_count: int
    timeout_cancelled_count: int
    completion_rate: float
    cancellation_rate: float
    timeout_rate: float


class HotSeatOut(BaseModel):
    seat_id: int
    seat_number: str
    floor: int
    area: str
    reservation_count: int


class HourlyOut(BaseModel):
    hour: int  # 0-23
    count: int


class ViolationStatsOut(BaseModel):
    total_violations: int
    by_type: Dict[str, int]
