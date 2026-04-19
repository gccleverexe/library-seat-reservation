from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.dependencies import get_current_user, success_response
from backend.schemas.reservation import ReservationCreate, ReservationOut
from backend.services import reservation_service
from backend.models.user import User

router = APIRouter()


@router.get("/history")
def get_history(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = reservation_service.get_history(db, current_user.id, status, page, page_size)
    return success_response(result)


@router.post("/", status_code=201)
def create_reservation(
    body: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = reservation_service.create_reservation(
        db, current_user.id, body.seat_id, body.start_time, body.end_time
    )
    return success_response(ReservationOut.model_validate(reservation), "预约成功", 201)


@router.delete("/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = reservation_service.cancel_reservation(
        db, reservation_id, current_user.id, is_admin=False
    )
    return success_response(ReservationOut.model_validate(reservation), "取消成功")
