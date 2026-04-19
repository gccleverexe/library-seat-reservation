from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.database import get_db
from backend.dependencies import get_current_user, success_response
from backend.schemas.seat import SeatOut
from backend.services import seat_service
from backend.models.user import User

router = APIRouter()


@router.get("/")
def list_seats(
    floor: Optional[int] = Query(None),
    area: Optional[str] = Query(None),
    time_start: Optional[datetime] = Query(None),
    time_end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seats = seat_service.list_seats(db, floor, area, time_start, time_end)
    return success_response([SeatOut.model_validate(s) for s in seats])


@router.get("/{seat_id}")
def get_seat(
    seat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seat = seat_service.get_seat(db, seat_id)
    return success_response(SeatOut.model_validate(seat))
