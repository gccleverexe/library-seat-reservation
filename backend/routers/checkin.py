from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user, success_response
from backend.schemas.reservation import CheckinRequest, CheckoutRequest, ReservationOut
from backend.services import checkin_service
from backend.models.user import User

router = APIRouter()


@router.post("/checkin")
def checkin(
    body: CheckinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = checkin_service.checkin(db, current_user.id, body.seat_number)
    return success_response(ReservationOut.model_validate(reservation), "签到成功")


@router.post("/checkout")
def checkout(
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = checkin_service.checkout(db, current_user.id, body.reservation_id)
    return success_response(ReservationOut.model_validate(reservation), "签退成功")
