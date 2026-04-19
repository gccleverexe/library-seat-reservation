import time
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.reservation import Reservation
from backend.models.seat import Seat
from backend.models.violation import Violation


def _check_timeout(start: float, limit: float = 5.0) -> None:
    if time.time() - start > limit:
        raise HTTPException(status_code=504, detail="查询超时，请缩小查询范围")


def get_summary(db: Session, date_from: Optional[str] = None, date_to: Optional[str] = None) -> dict:
    start = time.time()
    query = db.query(Reservation)

    if date_from:
        try:
            d = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Reservation.created_at >= d)
        except ValueError:
            pass
    if date_to:
        try:
            d = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Reservation.created_at <= d)
        except ValueError:
            pass

    _check_timeout(start)
    total = query.count()
    completed = query.filter(Reservation.status == "completed").count()
    cancelled = query.filter(Reservation.status == "cancelled").count()
    timeout_cancelled = query.filter(Reservation.status == "timeout_cancelled").count()

    _check_timeout(start)
    return {
        "total_reservations": total,
        "completed_count": completed,
        "cancelled_count": cancelled,
        "timeout_cancelled_count": timeout_cancelled,
        "completion_rate": round(completed / total, 4) if total > 0 else 0.0,
        "cancellation_rate": round(cancelled / total, 4) if total > 0 else 0.0,
        "timeout_rate": round(timeout_cancelled / total, 4) if total > 0 else 0.0,
    }


def get_hot_seats(db: Session) -> list:
    start = time.time()
    results = (
        db.query(
            Reservation.seat_id,
            func.count(Reservation.id).label("reservation_count"),
        )
        .group_by(Reservation.seat_id)
        .order_by(func.count(Reservation.id).desc())
        .limit(10)
        .all()
    )
    _check_timeout(start)

    items = []
    for row in results:
        seat = db.query(Seat).filter(Seat.id == row.seat_id).first()
        if seat:
            items.append({
                "seat_id": seat.id,
                "seat_number": seat.seat_number,
                "floor": seat.floor,
                "area": seat.area,
                "reservation_count": row.reservation_count,
            })
    return items


def get_hourly_distribution(db: Session) -> list:
    start = time.time()
    # SQLite: strftime('%H', datetime) returns hour as string
    results = (
        db.query(
            func.strftime("%H", Reservation.start_time).label("hour"),
            func.count(Reservation.id).label("count"),
        )
        .group_by(func.strftime("%H", Reservation.start_time))
        .all()
    )
    _check_timeout(start)

    # Build full 24-hour distribution
    hour_map = {int(r.hour): r.count for r in results}
    return [{"hour": h, "count": hour_map.get(h, 0)} for h in range(24)]


def get_violation_stats(db: Session, date_from: Optional[str] = None, date_to: Optional[str] = None) -> dict:
    start = time.time()
    query = db.query(Violation)

    if date_from:
        try:
            d = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Violation.created_at >= d)
        except ValueError:
            pass
    if date_to:
        try:
            d = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Violation.created_at <= d)
        except ValueError:
            pass

    _check_timeout(start)
    total = query.count()

    type_results = (
        db.query(Violation.type, func.count(Violation.id).label("count"))
        .group_by(Violation.type)
        .all()
    )
    _check_timeout(start)

    by_type = {r.type: r.count for r in type_results}
    return {"total_violations": total, "by_type": by_type}
