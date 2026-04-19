from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.reservation import Reservation
from backend.models.seat import Seat
from backend.models.user import User
from backend.services.seat_service import get_seat


def create_reservation(
    db: Session,
    user_id: int,
    seat_id: int,
    start_time: datetime,
    end_time: datetime,
) -> Reservation:
    # 1. Check seat exists
    seat = get_seat(db, seat_id)

    # 2. Check seat is not unavailable
    if seat.status == "unavailable":
        raise HTTPException(status_code=400, detail="该座位不可预约")

    # 3. Check duration <= 4 hours
    if (end_time - start_time) > timedelta(hours=4):
        raise HTTPException(status_code=400, detail="预约时长不能超过4小时")

    # 4. Check start_time < end_time
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="结束时间必须晚于开始时间")

    # 5. Check user restriction
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.is_restricted and user.restricted_until and user.restricted_until > datetime.utcnow():
        raise HTTPException(status_code=403, detail="您当前处于预约限制状态，无法预约")

    # 6. Check user already has active reservation
    existing = (
        db.query(Reservation)
        .filter(
            Reservation.user_id == user_id,
            Reservation.status.in_(("active", "checked_in")),
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="您已有一条有效预约，请先完成或取消后再预约")

    # 7. Check seat conflict
    conflict = (
        db.query(Reservation)
        .filter(
            Reservation.seat_id == seat_id,
            Reservation.status.in_(("active", "checked_in")),
            Reservation.start_time < end_time,
            Reservation.end_time > start_time,
        )
        .first()
    )
    if conflict:
        raise HTTPException(status_code=400, detail="该时段座位已被预约")

    # 8. Create reservation
    reservation = Reservation(
        user_id=user_id,
        seat_id=seat_id,
        start_time=start_time,
        end_time=end_time,
        status="active",
    )

    # 9. Update seat status
    seat.status = "reserved"

    # 10. Persist
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation_id: int, current_user_id: int, is_admin: bool = False) -> Reservation:
    # 1. Find reservation or 404
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="预约记录不存在")

    # 2. Permission check (non-admin can only cancel their own)
    if not is_admin and reservation.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="无权限取消此预约")

    # 3. Status check (can only cancel active reservations)
    if reservation.status in ("cancelled", "completed", "timeout_cancelled"):
        raise HTTPException(status_code=400, detail="该预约已结束，无法取消")

    # 4. Update reservation status
    reservation.status = "cancelled"

    # 5. Release seat (set back to available)
    seat = db.query(Seat).filter(Seat.id == reservation.seat_id).first()
    if seat:
        seat.status = "available"

    db.commit()
    db.refresh(reservation)
    return reservation


def get_history(
    db: Session,
    user_id: int,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Return paginated reservation history for a user, ordered by created_at desc."""
    query = (
        db.query(Reservation)
        .filter(Reservation.user_id == user_id)
    )
    if status:
        query = query.filter(Reservation.status == status)

    total = query.count()
    reservations = (
        query.order_by(Reservation.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Enrich with seat_number
    items = []
    for r in reservations:
        seat = db.query(Seat).filter(Seat.id == r.seat_id).first()
        item = {
            "id": r.id,
            "seat_id": r.seat_id,
            "seat_number": seat.seat_number if seat else None,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "status": r.status,
            "created_at": r.created_at,
        }
        items.append(item)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


def admin_list_reservations(
    db: Session,
    date: Optional[str] = None,  # YYYY-MM-DD
    seat_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Admin: list all reservations with optional filters."""
    query = db.query(Reservation)

    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(
                Reservation.start_time >= datetime.combine(d, datetime.min.time()),
                Reservation.start_time < datetime.combine(d, datetime.max.time()),
            )
        except ValueError:
            pass

    if seat_id:
        query = query.filter(Reservation.seat_id == seat_id)

    if status:
        query = query.filter(Reservation.status == status)

    total = query.count()
    reservations = (
        query.order_by(Reservation.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for r in reservations:
        seat = db.query(Seat).filter(Seat.id == r.seat_id).first()
        items.append({
            "id": r.id,
            "user_id": r.user_id,
            "seat_id": r.seat_id,
            "seat_number": seat.seat_number if seat else None,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "status": r.status,
            "created_at": r.created_at,
        })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


def admin_cancel_reservation(db: Session, reservation_id: int, admin_id: int) -> Reservation:
    """Admin: force cancel any reservation."""
    return cancel_reservation(db, reservation_id, admin_id, is_admin=True)


def get_violations(db: Session, student_id: int) -> list:
    """Get all violations for a student."""
    from backend.models.violation import Violation
    violations = (
        db.query(Violation)
        .filter(Violation.user_id == student_id)
        .order_by(Violation.created_at.desc())
        .all()
    )
    return violations


def lift_restriction(db: Session, student_id: int, admin_id: int) -> User:
    """Admin: lift reservation restriction for a student and log the action."""
    from backend.models.violation import OperationLog

    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_restricted = False
    user.restricted_until = None

    log = OperationLog(
        admin_id=admin_id,
        action="lift_restriction",
        target_type="user",
        target_id=student_id,
        detail=f"管理员解除用户 {user.campus_id} 的预约限制",
    )
    db.add(log)
    db.commit()
    db.refresh(user)
    return user
