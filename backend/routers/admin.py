from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import require_admin, success_response
from backend.schemas.seat import SeatOut, SeatCreate, SeatUpdate, SeatStatusUpdate
from backend.services import seat_service
from backend.models.user import User

router = APIRouter()


@router.post("/seats", status_code=201)
def create_seat(
    body: SeatCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    seat = seat_service.create_seat(db, body.seat_number, body.floor, body.area, body.description)
    return success_response(SeatOut.model_validate(seat), "座位创建成功", 201)


@router.put("/seats/{seat_id}")
def update_seat(
    seat_id: int,
    body: SeatUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    seat = seat_service.update_seat(
        db, seat_id,
        seat_number=body.seat_number,
        floor=body.floor,
        area=body.area,
        description=body.description,
    )
    return success_response(SeatOut.model_validate(seat), "座位更新成功")


@router.delete("/seats/{seat_id}")
def delete_seat(
    seat_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    seat_service.delete_seat(db, seat_id)
    return success_response(None, "座位删除成功")


@router.patch("/seats/{seat_id}/status")
def update_seat_status(
    seat_id: int,
    body: SeatStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    seat = seat_service.set_seat_status(db, seat_id, body.status)
    return success_response(SeatOut.model_validate(seat), "座位状态更新成功")


# --- Reservation management routes ---
from fastapi import Query
from typing import Optional
from backend.services import reservation_service
from backend.schemas.reservation import ReservationOut
from backend.schemas.auth import UserInfo


@router.get("/reservations")
def list_reservations(
    date: Optional[str] = Query(None),
    seat_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = reservation_service.admin_list_reservations(db, date, seat_id, status, page, page_size)
    return success_response(result)


@router.delete("/reservations/{reservation_id}")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    reservation = reservation_service.admin_cancel_reservation(db, reservation_id, admin.id)
    return success_response(ReservationOut.model_validate(reservation), "预约已取消")


@router.get("/violations")
def get_violations(
    student_id: int = Query(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    violations = reservation_service.get_violations(db, student_id)
    return success_response([
        {
            "id": v.id,
            "user_id": v.user_id,
            "reservation_id": v.reservation_id,
            "type": v.type,
            "note": v.note,
            "created_at": v.created_at,
        }
        for v in violations
    ])


@router.delete("/violations/{student_id}/restriction")
def lift_restriction(
    student_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = reservation_service.lift_restriction(db, student_id, admin.id)
    return success_response(UserInfo.model_validate(user), "预约限制已解除")


# --- Dashboard routes ---
from backend.services import dashboard_service


@router.get("/dashboard/summary")
def get_dashboard_summary(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = dashboard_service.get_summary(db, date_from, date_to)
    return success_response(result)


@router.get("/dashboard/hot-seats")
def get_hot_seats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = dashboard_service.get_hot_seats(db)
    return success_response(result)


@router.get("/dashboard/hourly")
def get_hourly_distribution(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = dashboard_service.get_hourly_distribution(db)
    return success_response(result)


@router.get("/dashboard/violations")
def get_violation_stats(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    result = dashboard_service.get_violation_stats(db, date_from, date_to)
    return success_response(result)
