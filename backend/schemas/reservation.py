from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    seat_id: int
    start_time: datetime
    end_time: datetime


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    seat_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime


class ReservationHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seat_id: int
    seat_number: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime


class ReservationListQuery(BaseModel):
    date: Optional[str] = None  # YYYY-MM-DD format
    seat_id: Optional[int] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class CheckinRequest(BaseModel):
    seat_number: str  # the checkin code


class CheckoutRequest(BaseModel):
    reservation_id: int
