import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.reservation import Reservation
from backend.models.seat import Seat
from backend.models.user import User
from backend.models.violation import Violation

logger = logging.getLogger(__name__)


def auto_release_expired_reservations() -> None:
    """
    Scan all 'active' reservations that have passed start_time + 15 minutes.
    For each expired reservation:
    1. Set reservation.status = 'timeout_cancelled'
    2. Set seat.status = 'available'
    3. Create a Violation record (type='no_checkin')
    4. Check if user has >= 3 violations → set is_restricted=True, restricted_until=now+7days
    """
    db: Session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(minutes=15)

        expired = (
            db.query(Reservation)
            .filter(
                Reservation.status == "active",
                Reservation.start_time <= cutoff,
            )
            .all()
        )

        for reservation in expired:
            # 1. Update reservation status
            reservation.status = "timeout_cancelled"

            # 2. Release seat
            seat = db.query(Seat).filter(Seat.id == reservation.seat_id).first()
            if seat:
                seat.status = "available"

            # 3. Create violation record
            violation = Violation(
                user_id=reservation.user_id,
                reservation_id=reservation.id,
                type="no_checkin",
                note="预约超时未签到，系统自动释放",
            )
            db.add(violation)
            db.flush()  # flush to get violation count

            # 4. Check violation count → restrict if >= 3
            violation_count = (
                db.query(Violation)
                .filter(Violation.user_id == reservation.user_id)
                .count()
            )
            if violation_count >= 3:
                user = db.query(User).filter(User.id == reservation.user_id).first()
                if user and not user.is_restricted:
                    user.is_restricted = True
                    user.restricted_until = datetime.utcnow() + timedelta(days=7)
                    logger.info(
                        f"User {user.campus_id} restricted for 7 days due to {violation_count} violations"
                    )

        db.commit()
        if expired:
            logger.info(f"Auto-released {len(expired)} expired reservations")

    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()
