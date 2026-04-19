from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.reservation import Reservation
from backend.models.seat import Seat


def list_seats(
    db: Session,
    floor: Optional[int] = None,
    area: Optional[str] = None,
    time_start: Optional[datetime] = None,
    time_end: Optional[datetime] = None,
) -> list[Seat]:
    query = db.query(Seat)

    if floor is not None:
        query = query.filter(Seat.floor == floor)

    if area is not None:
        query = query.filter(Seat.area == area)

    if time_start is not None and time_end is not None:
        # Exclude seats that have conflicting active/checked_in reservations
        conflicting_seat_ids = (
            db.query(Reservation.seat_id)
            .filter(
                Reservation.status.in_(("active", "checked_in")),
                Reservation.start_time < time_end,
                Reservation.end_time > time_start,
            )
            .subquery()
        )
        query = query.filter(Seat.id.notin_(conflicting_seat_ids))

    return query.all()


def get_seat(db: Session, seat_id: int) -> Seat:
    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not seat:
        raise HTTPException(status_code=404, detail="座位不存在")
    return seat


def create_seat(
    db: Session,
    seat_number: str,
    floor: int,
    area: str,
    description: Optional[str] = None,
) -> Seat:
    existing = db.query(Seat).filter(Seat.seat_number == seat_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="座位编号已存在")

    seat = Seat(
        seat_number=seat_number,
        floor=floor,
        area=area,
        description=description,
        status="available",
    )
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat


def update_seat(db: Session, seat_id: int, **kwargs) -> Seat:
    seat = get_seat(db, seat_id)

    for field, value in kwargs.items():
        if value is not None:
            setattr(seat, field, value)

    db.commit()
    db.refresh(seat)
    return seat


def delete_seat(db: Session, seat_id: int) -> None:
    seat = get_seat(db, seat_id)

    active_reservation = (
        db.query(Reservation)
        .filter(
            Reservation.seat_id == seat_id,
            Reservation.status.in_(("active", "checked_in")),
        )
        .first()
    )
    if active_reservation:
        raise HTTPException(status_code=400, detail="该座位存在有效预约，无法删除")

    db.delete(seat)
    db.commit()


def set_seat_status(db: Session, seat_id: int, status: str) -> Seat:
    seat = get_seat(db, seat_id)
    seat.status = status
    db.commit()
    db.refresh(seat)
    return seat
