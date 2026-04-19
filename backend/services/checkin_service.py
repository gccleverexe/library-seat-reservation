from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.reservation import Reservation
from backend.models.seat import Seat


def checkin(db: Session, user_id: int, seat_number: str) -> Reservation:
    # Find the user's active reservation
    reservation = (
        db.query(Reservation)
        .filter(Reservation.user_id == user_id, Reservation.status == "active")
        .first()
    )
    if not reservation:
        raise HTTPException(status_code=404, detail="未找到有效预约")

    # Find the seat by seat_number
    seat = db.query(Seat).filter(Seat.seat_number == seat_number).first()
    if not seat:
        raise HTTPException(status_code=404, detail="座位不存在")

    # Verify the reservation's seat_id matches the seat's id
    if reservation.seat_id != seat.id:
        raise HTTPException(status_code=400, detail="签到码与预约座位不匹配")

    # Check time window
    now = datetime.utcnow()
    window_start = reservation.start_time - timedelta(minutes=10)
    window_end = reservation.start_time + timedelta(minutes=15)

    if now < window_start:
        raise HTTPException(status_code=400, detail="签到时间未到，请在预约开始前10分钟内签到")
    if now > window_end:
        raise HTTPException(status_code=400, detail="签到超时，预约已自动释放")

    # Update statuses
    reservation.status = "checked_in"
    seat.status = "occupied"

    db.commit()
    db.refresh(reservation)
    return reservation


def checkout(db: Session, user_id: int, reservation_id: int) -> Reservation:
    # Find reservation by id
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约记录不存在")

    # Check ownership
    if reservation.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限操作此预约")

    # Check status
    if reservation.status != "checked_in":
        raise HTTPException(status_code=400, detail="该预约未处于签到状态")

    # Update reservation status
    reservation.status = "completed"

    # Release the seat
    seat = db.query(Seat).filter(Seat.id == reservation.seat_id).first()
    if seat:
        seat.status = "available"

    db.commit()
    db.refresh(reservation)
    return reservation
