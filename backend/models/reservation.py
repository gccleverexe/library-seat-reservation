from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, func

from backend.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="active")
    # active / checked_in / completed / cancelled / timeout_cancelled
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_reservations_user_status", "user_id", "status"),
        Index("ix_reservations_seat_time", "seat_id", "start_time", "end_time"),
        Index("ix_reservations_status_start", "status", "start_time"),
    )
